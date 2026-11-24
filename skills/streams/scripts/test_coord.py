"""Tests for coord.py: holds and their ends, refusals, OWED/PAID, local time across DST, the seat's
terminal and what `log` tells it.

    cd scripts && python3 -m unittest -v test_coord

Every test writes into a temporary COORD_DIR, never into a real repository's coord/, and `coord.term` is
replaced by a recorder, so no test reaches a terminal server.
"""
import datetime as dt
import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from zoneinfo import ZoneInfo

import coord

UTC = dt.timezone.utc
ZONE = ZoneInfo("Europe/Berlin")  # a zone with DST, standing in for the human's local time


def at(text):
    return dt.datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=UTC)


class CoordCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.join(self.tmp.name, "coord")
        self._env = {k: os.environ.get(k) for k in ("COORD_DIR", "COORD_AS", "TZ", "HC_TERMINAL_ID", "STREAMS_SEATS")}
        os.environ["COORD_DIR"] = self.dir
        os.environ["STREAMS_SEATS"] = os.path.join(self.tmp.name, "seats.json")
        os.environ.pop("COORD_AS", None)
        os.environ.pop("HC_TERMINAL_ID", None)
        self.sent = []       # what term.py was asked to send: (session, text)
        self.sessions = []   # what its `ls --json` lists
        self.send_exit = 0   # its exit code for `send`
        self._term, coord.term = coord.term, self.fake_term

    def fake_term(self, args, timeout=None):
        if args[0] == "ls":
            return 0, json.dumps({"server": "hc", "sessions": self.sessions}), ""
        if args[0] != "send":
            raise AssertionError(f"unexpected term.py call: {args}")
        if self.send_exit:
            return self.send_exit, "", "term: hc send failed: no such terminal"
        self.sent.append((args[1], args[2]))
        return 0, "", ""

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = coord.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def tearDown(self):
        coord.term = self._term
        for key, value in self._env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def log(self, text, who="alpha", now="2026-01-15 10:00", **kw):
        return coord.write(self.dir, text, who, now=at(now), zone=ZONE, **kw)

    def refused(self, text, who="alpha", now="2026-01-15 10:00", **kw):
        with self.assertRaises(coord.CoordError) as caught:
            self.log(text, who=who, now=now, **kw)
        return str(caught.exception)

    def holds(self):
        return coord.open_holds(coord.read_lines(self.dir))


class LineFormat(CoordCase):
    def test_line_is_dated_utc_with_who(self):
        line = self.log("deployed build 41 to stage")
        self.assertEqual(line, "2026-01-15 10:00 UTC alpha: deployed build 41 to stage")
        self.assertEqual(coord.read_lines(self.dir), [line])

    def test_multiline_text_becomes_one_line(self):
        self.assertTrue(self.log("one\n  two").endswith("alpha: one two"))

    def test_who_defaults_to_env(self):
        os.environ["COORD_AS"] = "seat"
        self.assertEqual(coord.default_who(), "seat")

    def test_who_with_space_is_refused(self):
        self.assertIn("one word", self.refused("x", who="two words"))

    def test_coord_dir_override(self):
        self.assertEqual(coord.coord_dir(), os.path.abspath(self.dir))

    def test_coord_dir_is_shared_by_worktrees(self):
        os.environ.pop("COORD_DIR")
        repo = os.path.join(self.tmp.name, "repo")
        tree = os.path.join(self.tmp.name, "repo-side")
        quiet = {"capture_output": True, "check": True}
        subprocess.run(["git", "init", "-q", repo], **quiet)
        subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "--allow-empty", "-m", "start"], **quiet)
        subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "-b", "side", tree], **quiet)
        main_dir = coord.coord_dir(cwd=repo)
        self.assertEqual(main_dir, os.path.join(os.path.realpath(repo), ".git", "coord"))
        self.assertEqual(coord.coord_dir(cwd=tree), main_dir)
        self.assertEqual(coord.default_who(cwd=tree), "repo-side")


class Holds(CoordCase):
    def test_hold_without_end_is_refused(self):
        self.assertIn("needs an end", self.refused("HOLD stage: deploying"))
        self.assertEqual(coord.read_lines(self.dir), [])

    def test_hold_for_stores_end_last(self):
        line = self.log("HOLD stage: deploying", for_="40m")
        self.assertTrue(line.endswith("HOLD stage: deploying until 2026-01-15 10:40 UTC"))
        [hold] = self.holds()
        self.assertEqual((hold["what"], hold["who"], hold["end"]), ("stage", "alpha", at("2026-01-15 10:40")))

    def test_durations(self):
        self.assertEqual(coord.parse_duration("1h30m"), dt.timedelta(minutes=90))
        self.assertEqual(coord.parse_duration("2h"), dt.timedelta(hours=2))
        self.assertEqual(coord.parse_duration("90"), dt.timedelta(minutes=90))
        self.assertIsNone(coord.parse_duration("soon"))
        self.assertIn("not a length", self.refused("HOLD stage: x", for_="soon"))

    def test_both_ends_refused(self):
        self.assertIn("once", self.refused("HOLD stage: x", for_="40m", until="12:00"))

    def test_end_on_non_hold_refused(self):
        self.assertIn("HOLD line only", self.refused("deployed", for_="40m"))
        self.assertIn("HOLD line only", self.refused("RELEASE stage: done", for_="40m"))

    def test_hold_without_what_refused(self):
        self.assertIn("names what", self.refused("HOLD: deploying", for_="40m"))
        self.assertIn("names what", self.refused("HOLD — deploying", for_="40m"))

    def test_what_strips_punctuation_and_case(self):
        self.log("HOLD Stage, for the night", for_="1h")
        self.assertEqual(self.holds()[0]["what"], "Stage")
        self.log("RELEASE stage.: done", now="2026-01-15 10:10")
        self.assertEqual(self.holds(), [])

    def test_lower_case_is_normalized(self):
        line = self.log("hold stage: x", for_="10m")
        self.assertIn("alpha: HOLD stage: x until", line)
        line = self.log("release stage: done", now="2026-01-15 10:05")
        self.assertIn("alpha: RELEASE stage: done", line)
        self.assertEqual(self.holds(), [])

    def test_lower_case_hold_without_end_refused(self):
        self.assertIn("needs an end", self.refused("hold stage: x"))

    def test_second_holder_refused_naming_holder_end_and_release(self):
        self.log("HOLD stage: deploying", for_="40m")
        msg = self.refused("HOLD stage: me too", who="beta", now="2026-01-15 10:10", for_="10m")
        self.assertIn("held by alpha until 11:40 CET", msg)
        self.assertIn('log "RELEASE stage: <why>"', msg)

    def test_same_holder_moves_end_keeps_since(self):
        self.log("HOLD stage: deploying", for_="40m")
        self.log("HOLD stage: still deploying", now="2026-01-15 10:30", for_="1h")
        [hold] = self.holds()
        self.assertEqual(hold["end"], at("2026-01-15 11:30"))
        self.assertEqual(hold["since"], at("2026-01-15 10:00"))

    def test_expired_hold_stays_and_anyone_may_take_it(self):
        self.log("HOLD stage: deploying", for_="20m")
        self.assertEqual(len(self.holds()), 1)  # nothing releases on its own
        self.log("HOLD stage: mine now", who="beta", now="2026-01-15 11:00", for_="30m")
        [hold] = self.holds()
        self.assertEqual((hold["who"], hold["since"]), ("beta", at("2026-01-15 11:00")))

    def test_anyone_may_release(self):
        self.log("HOLD stage: deploying", for_="40m")
        self.log("RELEASE stage: alpha's session is gone", who="seat", now="2026-01-15 10:05")
        self.assertEqual(self.holds(), [])
        self.log("HOLD stage: next", who="beta", now="2026-01-15 10:06", for_="5m")

    def test_old_release_wordings(self):
        self.log("HOLD stage: x", for_="40m")
        self.assertIn("RELEASE stage", self.refused("HOLD stage released", now="2026-01-15 10:01"))
        self.log("RELEASED stage after the deploy", now="2026-01-15 10:02")
        self.assertEqual(self.holds(), [])

    def test_release_without_what_refused(self):
        self.assertIn("names what", self.refused("RELEASE: done"))

    def test_hold_line_without_end_in_log_is_not_listed(self):
        os.makedirs(self.dir)
        with open(os.path.join(self.dir, coord.LOG), "w") as f:
            f.write("2026-01-14 09:00 UTC alpha: HOLD stage: written by hand, no end\n")
        self.assertEqual(self.holds(), [])

    def test_show_lists_live_and_expired(self):
        self.log("HOLD stage: deploying", for_="40m")
        self.log("HOLD lab: a long run", who="beta", for_="10m")
        out = coord.show(self.dir, now=at("2026-01-15 10:20"), zone=ZONE)
        live, expired = out.split("EXPIRED HOLDS")
        self.assertIn("stage  by alpha", live)
        self.assertIn("(20m left)", live)
        self.assertIn("lab  by beta, ended 11:10 CET (10m ago)", expired)
        self.assertIn("LOG (newest 2)", out)

    def test_show_holds_only(self):
        self.log("deployed")
        out = coord.show(self.dir, holds=True, now=at("2026-01-15 10:20"), zone=ZONE)
        self.assertNotIn("OWED", out)
        self.assertNotIn("LOG", out)


class LocalTime(CoordCase):
    def test_until_is_next_local_time_winter(self):
        # 10:00 UTC is 11:00 CET; 12:30 CET is 11:30 UTC the same day.
        line = self.log("HOLD stage: x", until="12:30")
        self.assertTrue(line.endswith("until 2026-01-15 11:30 UTC"))

    def test_until_already_passed_today_means_tomorrow(self):
        line = self.log("HOLD stage: x", until="07:30")
        self.assertTrue(line.endswith("until 2026-01-16 06:30 UTC"))

    def test_until_summer(self):
        line = self.log("HOLD stage: x", now="2026-07-01 10:00", until="12:30")
        self.assertTrue(line.endswith("until 2026-07-01 10:30 UTC"))

    def test_skipped_time_refused(self):
        # 2026-03-29: the zone's clocks go from 02:00 to 03:00.
        msg = self.refused("HOLD stage: x", now="2026-03-28 22:00", until="02:30")
        self.assertIn("does not exist on 2026-03-29", msg)

    def test_skipped_time_behind_us_takes_the_next_day(self):
        line = self.log("HOLD stage: x", now="2026-03-29 08:00", until="02:30")
        self.assertTrue(line.endswith("until 2026-03-30 00:30 UTC"))

    def test_repeated_time_means_the_first(self):
        # 2026-10-25: the zone's clocks go from 03:00 back to 02:00; 02:30 comes at 00:30 and 01:30 UTC.
        line = self.log("HOLD stage: x", now="2026-10-24 20:00", until="02:30")
        self.assertTrue(line.endswith("until 2026-10-25 00:30 UTC"))

    def test_repeated_time_between_the_two_is_the_second(self):
        line = self.log("HOLD stage: x", now="2026-10-25 00:45", until="02:30")
        self.assertTrue(line.endswith("until 2026-10-25 01:30 UTC"))

    def test_bad_clock_refused(self):
        self.assertIn("not a time", self.refused("HOLD stage: x", until="25:00"))

    def test_tz_env_names_the_zone(self):
        os.environ["TZ"] = "America/New_York"
        self.assertEqual(coord.local_zone(), ZoneInfo("America/New_York"))


class OwedPaid(CoordCase):
    def test_owed_gets_next_free_id(self):
        first = self.log("OWED beta: the deploy answer", who="seat")
        second = self.log("OWED gamma: relay the table", who="seat")
        self.assertIn("seat: OWED a1 beta: the deploy answer", first)
        self.assertIn("seat: OWED a2 gamma: relay the table", second)
        self.log("PAID a1 answered", who="seat")
        third = self.log("OWED beta: one more", who="seat")
        self.assertIn("OWED a3 beta", third)  # ids are never reused
        unpaid = coord.open_owed(coord.read_lines(self.dir))
        self.assertEqual([o["id"] for o in unpaid], ["a2", "a3"])

    def test_paid_unknown_or_twice_refused(self):
        self.assertIn("No OWED line has the id a9", self.refused("PAID a9"))
        self.log("OWED beta: x", who="seat")
        self.log("PAID a1")
        self.assertIn("already paid", self.refused("PAID a1"))

    def test_owed_needs_stream_and_what(self):
        self.assertIn("names the stream", self.refused("OWED beta"))
        self.assertIn("gives an OWED line its id", self.refused("OWED a4 beta: x"))

    def test_show_owed(self):
        self.log("OWED beta: the deploy answer", who="seat")
        out = coord.show(self.dir, owed=True, now=at("2026-01-15 11:30"), zone=ZONE)
        self.assertIn("a1  beta, waiting 1h30m: the deploy answer", out)


class Command(CoordCase):
    def test_init_creates_files_once(self):
        code, out, _ = self.run_main("init")
        self.assertEqual(code, 0)
        for name in (coord.STREAMS, coord.LOG, coord.ASKS, coord.SCHEDULES):
            self.assertTrue(os.path.exists(os.path.join(self.dir, name)), name)
        self.assertTrue(os.path.isdir(os.path.join(self.dir, coord.ROADMAPS)))
        code, out, _ = self.run_main("init")
        self.assertIn("nothing written", out)

    def test_hold_without_end_exits_2(self):
        code, _, err = self.run_main("log", "HOLD stage: x", "--as", "alpha")
        self.assertEqual(code, 2)
        self.assertIn("--for", err)

    def test_log_and_show(self):
        os.environ["COORD_AS"] = "seat"
        code, out, _ = self.run_main("log", "OWED beta: x")
        self.assertEqual(code, 0)
        self.assertIn('"PAID a1"', out)
        code, out, _ = self.run_main("show", "--log", "1")
        self.assertIn("seat: OWED a1 beta: x", out)
        self.assertNotIn("HOLDS", out)


class Seat(CoordCase):
    def seat_file(self):
        with open(os.path.join(self.dir, coord.SEAT)) as f:
            return json.load(f)

    def test_none_registered(self):
        code, out, _ = self.run_main("seat")
        self.assertEqual(code, 0)
        self.assertIn("seat: not registered\n", out)
        self.assertIn("seat --here", out)
        self.assertIsNone(coord.read_seat(self.dir))

    def test_set_stores_session_and_utc_time(self):
        code, out, _ = self.run_main("seat", "--set", "t7")
        self.assertEqual(code, 0)
        stored = self.seat_file()
        self.assertEqual(stored["session"], "t7")
        self.assertRegex(stored["set"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC$")
        self.assertEqual(out, f"seat: t7 (set {stored['set']})\n")
        self.assertEqual(self.run_main("seat")[1], out)
        self.assertEqual(coord.set_seat(self.dir, "t8", now=at("2026-01-15 10:00")),
                         {"session": "t8", "set": "2026-01-15 10:00 UTC"})
        self.assertEqual(self.seat_file()["session"], "t8")  # a new registration replaces the old one

    def test_set_refuses_what_is_no_session_id(self):
        code, _, err = self.run_main("seat", "--set", "two words")
        self.assertEqual(code, 2)
        self.assertIn("not a session id", err)
        self.assertIsNone(coord.read_seat(self.dir))

    def test_here_registers_this_terminal(self):
        os.environ["HC_TERMINAL_ID"] = "t17"
        code, out, _ = self.run_main("seat", "--here")
        self.assertEqual(code, 0)
        self.assertIn("seat: t17 (set ", out)
        self.assertEqual(self.seat_file()["session"], "t17")

    def test_here_without_the_variable_is_refused(self):
        code, out, err = self.run_main("seat", "--here")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("HC_TERMINAL_ID is not set", err)
        self.assertIn("seat --set <session>", err)
        self.assertFalse(os.path.exists(os.path.join(self.dir, coord.SEAT)))

    def test_clear(self):
        self.run_main("seat", "--set", "t7")
        self.assertEqual(self.run_main("seat", "--clear"), (0, "seat: cleared (was t7)\n", ""))
        self.assertFalse(os.path.exists(os.path.join(self.dir, coord.SEAT)))
        self.assertIn("not registered", self.run_main("seat")[1])
        self.assertEqual(self.run_main("seat", "--clear")[1], "seat: not registered; nothing to clear\n")

    def test_an_unreadable_file_reads_as_not_registered(self):
        os.makedirs(self.dir)
        with open(os.path.join(self.dir, coord.SEAT), "w") as f:
            f.write("{half a file")
        self.assertIsNone(coord.read_seat(self.dir))

    def test_show_names_the_seat(self):
        self.log("OWED beta: x", who="seat")
        self.assertEqual(self.run_main("show")[1].splitlines()[1], "seat: not registered")
        self.assertEqual(self.run_main("show", "--owed")[1].splitlines()[1], "seat: not registered")
        coord.set_seat(self.dir, "t7", now=at("2026-01-15 10:00"))
        want = "seat: t7 (set 2026-01-15 10:00 UTC)"
        self.assertEqual(self.run_main("show")[1].splitlines()[1], want)
        self.assertEqual(self.run_main("show", "--owed")[1].splitlines()[1:3], [want, "OWED"])
        self.assertNotIn("seat:", self.run_main("show", "--holds")[1])
        self.assertEqual(self.run_main("show", "--log", "1")[1].splitlines()[1], "LOG (newest 1)")


class SeveralRepos(CoordCase):
    """One seat serving two repositories: -C, the user's seats file, and `repos`."""

    def setUp(self):
        super().setUp()
        os.environ.pop("COORD_DIR")
        quiet = {"capture_output": True, "check": True}
        self.a = os.path.realpath(os.path.join(self.tmp.name, "alpha"))
        self.b = os.path.realpath(os.path.join(self.tmp.name, "beta"))
        for repo in (self.a, self.b):
            subprocess.run(["git", "init", "-q", repo], **quiet)
            subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                            "--allow-empty", "-m", "start"], **quiet)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.a)

    def test_one_seat_two_repositories(self):
        self.assertEqual(self.run_main("seat", "--set", "t1")[0], 0)
        self.assertEqual(self.run_main("-C", self.b, "seat", "--set", "t1")[0], 0)
        self.assertEqual(coord.read_seat(os.path.join(self.b, ".git", "coord"))["session"], "t1")
        code, out, _ = self.run_main("repos", "--seat", "t1", "--paths")
        self.assertEqual((code, out.split()), (0, [self.a, self.b]))

    def test_here_records_the_repository(self):
        os.environ["HC_TERMINAL_ID"] = "t9"
        self.run_main("-C", self.b, "seat", "--here")
        self.assertEqual(self.run_main("repos", "--paths")[1].split(), [self.b])

    def test_a_repository_has_one_seat(self):
        self.run_main("seat", "--set", "t1")
        self.run_main("-C", self.b, "seat", "--set", "t1")
        self.run_main("-C", self.b, "seat", "--set", "t2")
        self.assertEqual(self.run_main("repos", "--seat", "t1", "--paths")[1].split(), [self.a])
        self.assertEqual(self.run_main("repos", "--seat", "t2", "--paths")[1].split(), [self.b])

    def test_moved_registration_is_shown_not_listed(self):
        self.run_main("seat", "--set", "t1")
        coord.set_seat(os.path.join(self.a, ".git", "coord"), "t3")   # changed behind the file's back
        self.assertIn("moved to t3", self.run_main("repos", "--seat", "t1")[1])
        self.assertEqual(self.run_main("repos", "--seat", "t1", "--paths")[1], "")

    def test_clear_forgets_the_repository(self):
        self.run_main("seat", "--set", "t1")
        self.run_main("-C", self.b, "seat", "--set", "t1")
        self.run_main("-C", self.b, "seat", "--clear")
        self.assertEqual(self.run_main("repos", "--seat", "t1", "--paths")[1].split(), [self.a])

    def test_repos_defaults_to_the_seat_registered_here(self):
        self.run_main("seat", "--set", "t1")
        self.assertIn(self.a, self.run_main("repos")[1])

    def test_hint_carries_c(self):
        out = self.run_main("-C", self.b, "log", "OWED beta: x", "--no-tell")[1]
        self.assertIn(f"-C {self.b}", out.replace(os.path.expanduser("~"), "~").replace("~", os.path.expanduser("~")))

    def test_c_to_a_missing_directory_is_refused(self):
        code, _, err = self.run_main("-C", os.path.join(self.tmp.name, "nope"), "show")
        self.assertEqual(code, 2)
        self.assertIn("no such directory", err)

    def test_log_with_c_writes_in_that_repository(self):
        self.run_main("-C", self.b, "log", "note in beta", "--no-tell")
        with open(os.path.join(self.b, ".git", "coord", "log.md"), encoding="utf-8") as f:
            self.assertIn("note in beta", f.read())
        self.assertFalse(os.path.exists(os.path.join(self.a, ".git", "coord", "log.md")))


class Relay(CoordCase):
    """What `log` tells a terminal once the line is written. The seat is t1; the stream beta works in t5."""

    def setUp(self):
        super().setUp()
        coord.set_seat(self.dir, "t1")

    def streams(self):
        """A repository `demo` with the worktree `demo-beta`, a session in each, and the main checkout as cwd."""
        repo = os.path.join(self.tmp.name, "work", "demo")
        tree = os.path.join(self.tmp.name, "work", "demo-beta")
        quiet = {"capture_output": True, "check": True}
        subprocess.run(["git", "init", "-q", repo], **quiet)
        subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "--allow-empty", "-m", "start"], **quiet)
        subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "-b", "beta", tree], **quiet)
        os.makedirs(os.path.join(tree, "src"))
        self.sessions = [{"id": "t1", "cwd": repo, "agent": "claude"},
                         {"id": "t4", "cwd": os.path.join(tree, "src"), "agent": "bash"},
                         {"id": "t5", "cwd": tree, "agent": "claude"}]
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(repo)
        return repo, tree

    def logged(self):
        return [coord.parse_line(line)[2] for line in coord.read_lines(self.dir)]

    def test_owed_goes_to_the_seat(self):
        code, out, err = self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.sent, [("t1", "demo-beta: OWED a1 beta: the deploy answer")])
        self.assertEqual(out.splitlines()[-1], "told t1")
        self.assertIn("demo-beta: OWED a1 beta: the deploy answer", out.splitlines()[0])
        self.assertEqual(self.logged(), ["OWED a1 beta: the deploy answer"])

    def test_owed_without_a_seat_is_logged_and_says_how_to_register(self):
        coord.clear_seat(self.dir)
        code, out, err = self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta")
        self.assertEqual(code, 0)
        self.assertIn("not delivered: no seat is registered", err)
        self.assertIn("seat --here", err)
        self.assertEqual(len(err.splitlines()), 1)
        self.assertNotIn("told", out)
        self.assertEqual((self.sent, self.logged()), ([], ["OWED a1 beta: the deploy answer"]))

    def test_paid_goes_to_the_stream_that_wrote_the_owed_line(self):
        self.streams()
        self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta")
        code, out, err = self.run_main("log", "PAID a1", "--as", "seat")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.sent[-1], ("t5", "PAID a1: the deploy answer"))  # the Claude session, not the shell
        self.assertEqual(out.splitlines()[-1], "told t5")
        self.assertEqual(coord.open_owed(coord.read_lines(self.dir)), [])

    def test_paid_with_a_note_closes_the_line_and_relays_the_note(self):
        self.streams()
        self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta")
        code, _, err = self.run_main("log", "PAID a1: build 41 is on stage", "--as", "seat")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.sent[-1], ("t5", "PAID a1: the deploy answer -- build 41 is on stage"))
        self.assertEqual(self.logged()[-1], "PAID a1: build 41 is on stage")
        self.assertEqual(coord.open_owed(coord.read_lines(self.dir)), [])
        self.assertIn("already paid", self.refused("PAID a1: again"))

    def test_paid_on_the_seats_own_owed_line_goes_to_the_stream_it_names(self):
        self.streams()
        os.environ["HC_TERMINAL_ID"] = "t1"
        self.run_main("log", "OWED beta: relay the table", "--as", "seat")
        self.assertEqual(self.sent, [])  # the seat does not tell itself
        self.run_main("log", "PAID a1 relayed", "--as", "seat")
        self.assertEqual(self.sent, [("t5", "PAID a1: relay the table -- relayed")])

    def test_paid_with_no_session_for_the_stream_is_logged(self):
        self.streams()
        self.sessions = self.sessions[:1]
        self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta")
        code, out, err = self.run_main("log", "PAID a1", "--as", "seat")
        self.assertEqual(code, 0)
        self.assertIn("not delivered: no session found for the stream demo-beta", err)
        self.assertNotIn("told", out)
        self.assertEqual(self.logged()[-1], "PAID a1")

    def test_paid_for_a_writer_with_no_worktree_is_logged(self):
        self.streams()
        self.run_main("log", "OWED gamma: x", "--as", "gamma", "--no-tell")
        code, _, err = self.run_main("log", "PAID a1", "--as", "seat")
        self.assertEqual(code, 0)
        self.assertIn("no session found for the stream gamma: no worktree", err)
        self.assertEqual(self.logged()[-1], "PAID a1")

    def test_a_session_belongs_to_the_deepest_worktree_around_its_cwd(self):
        trees = ["/w/demo", "/w/demo/trees/demo-beta"]
        listed = [{"id": "t1", "cwd": "/w/demo/docs"}, {"id": "t5", "cwd": "/w/demo/trees/demo-beta"},
                  {"id": "t6", "cwd": "/home/x", "foreground_cwd": "/w/demo/trees/demo-beta"}]
        self.assertEqual(coord.stream_session(trees[0], trees, listed), "t1")
        self.assertEqual(coord.stream_session(trees[1], trees, listed), "t5")
        self.assertEqual(coord.stream_session(trees[1], trees, listed[::2]), "t6")  # by its foreground program
        self.assertIsNone(coord.stream_session(trees[1], trees, listed[:1]))
        self.assertEqual(coord.stream_worktree("beta", trees), trees[1])
        self.assertEqual(coord.stream_worktree("demo-beta", trees), trees[1])
        self.assertIsNone(coord.stream_worktree("gamma", trees))

    def test_tell_seat_relays_any_line(self):
        code, out, err = self.run_main("log", "loop 3: kept, 0.71 on the ruler", "--tell", "seat", "--as", "demo-beta")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.sent, [("t1", "demo-beta: loop 3: kept, 0.71 on the ruler")])
        self.assertEqual(out.splitlines()[-1], "told t1")

    def test_tell_a_stream_by_slug_or_a_session_by_id(self):
        self.streams()
        self.run_main("log", "the trunk moved; sync when it suits you", "--tell", "beta", "--as", "seat")
        self.run_main("log", "deployed build 41", "--tell", "t9", "--as", "seat")
        self.assertEqual(self.sent, [("t5", "seat: the trunk moved; sync when it suits you"),
                                     ("t9", "seat: deployed build 41")])

    def test_a_plain_line_tells_nobody(self):
        code, out, err = self.run_main("log", "deployed build 41", "--as", "demo-beta")
        self.assertEqual((code, err, self.sent), (0, "", []))
        self.assertNotIn("told", out)

    def test_no_tell_suppresses_the_relay(self):
        code, out, err = self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta", "--no-tell")
        self.assertEqual((code, err, self.sent), (0, "", []))
        self.assertNotIn("told", out)
        self.assertEqual(self.logged(), ["OWED a1 beta: the deploy answer"])
        coord.clear_seat(self.dir)  # and no complaint about a seat it did not need
        self.assertEqual(self.run_main("log", "OWED beta: more", "--as", "demo-beta", "--no-tell")[2], "")

    def test_never_tells_the_terminal_it_runs_in(self):
        os.environ["HC_TERMINAL_ID"] = "t1"
        code, out, err = self.run_main("log", "OWED beta: relay the table", "--as", "seat")
        self.assertEqual((code, err, self.sent), (0, "", []))
        self.assertNotIn("told", out)
        self.run_main("log", "a note to myself", "--tell", "seat", "--as", "seat")
        self.run_main("log", "a note to myself", "--tell", "t1", "--as", "seat")
        self.assertEqual(self.sent, [])
        self.assertEqual(len(self.logged()), 3)

    def test_a_failing_sender_leaves_the_line_and_exits_0(self):
        self.send_exit = 1
        code, out, err = self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta")
        self.assertEqual(code, 0)
        self.assertEqual(err, "coord log: written, not delivered: term.py send t1 exited 1: "
                              "term: hc send failed: no such terminal\n")
        self.assertNotIn("told", out)
        self.assertIn("OWED a1 beta: the deploy answer", out)
        self.assertEqual(self.logged(), ["OWED a1 beta: the deploy answer"])

    def test_a_sender_that_raises_leaves_the_line_and_exits_0(self):
        def broken(args, timeout=None):
            raise RuntimeError("no such door")
        coord.term = broken
        code, _, err = self.run_main("log", "OWED beta: the deploy answer", "--as", "demo-beta")
        self.assertEqual(code, 0)
        self.assertIn("not delivered: RuntimeError: no such door", err)
        self.assertEqual(self.logged(), ["OWED a1 beta: the deploy answer"])

    def test_a_refused_line_tells_nobody(self):
        code, _, _ = self.run_main("log", "PAID a9", "--tell", "seat", "--as", "seat")
        self.assertEqual((code, self.sent, self.logged()), (2, [], []))

    def test_tell_and_no_tell_together_are_refused_before_anything_is_written(self):
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            coord.main(["log", "x", "--tell", "seat", "--no-tell"])
        self.assertEqual(self.logged(), [])

    def test_the_real_sender_runs_term_py_beside_coord_py(self):
        code, out, _ = self._term(["--help"])  # argparse answers before any server is asked
        self.assertEqual(code, 0)
        self.assertIn("term.py", out)


class ProjectConfig(CoordCase):
    """`config` and `init-file` against scratch repositories in the temporary directory."""

    def git(self, *args, cwd=None):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                              capture_output=True, text=True, check=True).stdout.strip()

    def repo(self, name="demo", branch="main"):
        path = os.path.join(self.tmp.name, "work", name)
        os.makedirs(path)
        self.git("init", "-q", "-b", branch, path)
        self.git("commit", "-q", "--allow-empty", "-m", "start", cwd=path)
        return os.path.realpath(path)

    def write_file(self, repo, text, rel=".devmeta/streams.md"):
        path = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def run_in(self, cwd, *argv):
        out, err = io.StringIO(), io.StringIO()
        here = os.getcwd()
        os.chdir(cwd)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = coord.main(list(argv))
        finally:
            os.chdir(here)
        return code, out.getvalue(), err.getvalue()

    def test_main_without_file_gives_defaults(self):
        repo = self.repo()
        facts = coord.config(cwd=repo)
        self.assertIsNone(facts["file"])
        self.assertEqual(facts["trunk"]["value"], "main")
        self.assertIn("detected", facts["trunk"]["source"])
        self.assertEqual(facts["worktree_root"]["value"], os.path.dirname(repo))
        self.assertEqual(facts["at_cut"]["value"], "")
        self.assertEqual(facts["at_landing"]["value"], "")
        self.assertEqual((facts["resources"], facts["warnings"]), ("", []))

    def test_master_only_and_odd_branch(self):
        self.assertEqual(coord.config(cwd=self.repo("a", "master"))["trunk"]["value"], "master")
        odd = coord.config(cwd=self.repo("b", "develop"))["trunk"]
        self.assertEqual((odd["value"], odd["source"]), ("develop", "detected: the current branch"))

    def test_origin_head_names_the_trunk(self):
        upstream = self.repo("up", "trunk")
        clone = os.path.join(self.tmp.name, "work", "clone")
        self.git("clone", "-q", upstream, clone)
        self.git("checkout", "-q", "-b", "main", cwd=clone)  # a local main must not win over origin's HEAD
        facts = coord.config(cwd=clone)
        self.assertEqual(facts["trunk"]["value"], "trunk")
        self.assertIn("origin/HEAD", facts["trunk"]["source"])

    def test_file_trunk_wins_over_detection(self):
        repo = self.repo()
        self.write_file(repo, "## Project\ntrunk: release   # the branch production builds\n")
        facts = coord.config(cwd=repo)
        self.assertEqual(facts["trunk"]["value"], "release")
        self.assertIn("## Project", facts["trunk"]["source"])

    def test_worktree_root_outside_parent_and_slug(self):
        repo = self.repo()
        outside = os.path.join(self.tmp.name, "elsewhere", "trees")
        self.write_file(repo, f"## Project\nworktree root: {outside}\n")
        facts = coord.config(cwd=repo, slug="demo")
        self.assertEqual(facts["worktree_root"]["value"], outside)
        self.assertEqual(facts["worktree"], os.path.join(outside, "demo-demo"))
        code, out, _ = self.run_in(repo, "config", "--slug", "demo")
        self.assertEqual(code, 0)
        self.assertIn(f"worktree: {os.path.join(outside, 'demo-demo')}", out)

    def test_tilde_root_is_expanded(self):
        repo = self.repo()
        self.write_file(repo, "## Project\nworktree root: ~/trees\n")
        self.assertEqual(coord.config(cwd=repo)["worktree_root"]["value"], os.path.expanduser("~/trees"))

    def test_default_slug_path_is_beside_the_repo(self):
        repo = self.repo()
        facts = coord.config(cwd=repo, slug="side")
        self.assertEqual(facts["worktree"], os.path.join(os.path.dirname(repo), "demo-side"))

    def test_worktree_names_follow_the_main_checkout(self):
        repo = self.repo()
        tree = os.path.join(self.tmp.name, "work", "demo-side")
        self.git("worktree", "add", "-q", "-b", "side", tree, cwd=repo)
        facts = coord.config(cwd=tree, slug="next")
        self.assertEqual(facts["worktree"], os.path.join(os.path.dirname(repo), "demo-next"))

    def test_sections_bodies_resources_and_unknown_warning(self):
        repo = self.repo()
        self.write_file(repo, "# title\n\n## At cut\nnpm ci\ncp .env.example .env\n\n## At landing\nnpm test\n\n"
                              "## Resources\nweb: 70k0\n\n## Wishes\nsomething\n")
        facts = coord.config(cwd=repo)
        self.assertEqual(facts["at_cut"]["value"], "npm ci\ncp .env.example .env")
        self.assertEqual(facts["at_landing"]["value"], "npm test")
        self.assertEqual(facts["resources"], "web: 70k0")
        [warning] = facts["warnings"]
        self.assertIn("## Wishes", warning)
        code, out, _ = self.run_in(repo, "config")
        self.assertEqual(code, 0)
        self.assertIn("warning: unknown section '## Wishes'", out)

    def test_at_landing_defaults_to_tick_testing(self):
        repo = self.repo()
        self.write_file(repo, "## Testing\n\nmake test\n", rel=".tick/config.md")
        facts = coord.config(cwd=repo)
        self.assertEqual(facts["at_landing"]["value"], "")  # prose, not a command line
        self.assertIn("default", facts["at_landing"]["source"])
        code, out, err = self.run_in(repo, "config", "--get", "at-landing")
        self.assertEqual((code, out), (0, ""))
        self.assertIn(".tick/config.md", err)
        self.assertIn("at_landing: see .tick/config.md → ## Testing", self.run_in(repo, "config")[1])

    def test_get_trunk_with_nothing_detected_fails(self):
        repo = self.repo("lone", "develop")
        self.git("checkout", "-q", "--detach", cwd=repo)
        self.git("branch", "-q", "-D", "develop", cwd=repo)
        code, out, err = self.run_in(repo, "config", "--get", "trunk")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("no trunk", err)

    def test_headings_inside_a_fence_are_body_and_one_fence_is_stripped(self):
        repo = self.repo()
        self.write_file(repo, "## At cut\n\n```sh\n## install first\nuv sync\n```\n\n## At landing\nmake test\n")
        facts = coord.config(cwd=repo)
        self.assertEqual(facts["at_cut"]["value"], "## install first\nuv sync")
        self.assertEqual(facts["at_landing"]["value"], "make test")
        self.assertEqual(facts["warnings"], [])

    def test_a_worktree_reads_the_main_checkouts_file(self):
        repo = self.repo()
        self.write_file(repo, "## Project\nworktree root: trees\n")
        tree = os.path.join(self.tmp.name, "work", "demo-side")
        self.git("worktree", "add", "-q", "-b", "side", tree, cwd=repo)
        self.write_file(tree, "## Project\nworktree root: other\n")  # the branch's own copy differs
        facts = coord.config(cwd=tree)
        self.assertEqual(facts["worktree_root"]["value"], os.path.join(repo, "trees"))
        self.assertEqual(facts["file"], os.path.join(repo, ".devmeta", "streams.md"))

    def test_json(self):
        repo = self.repo()
        code, out, _ = self.run_in(repo, "config", "--json", "--slug", "x")
        facts = json.loads(out)
        self.assertEqual((code, facts["trunk"]["value"]), (0, "main"))
        self.assertTrue(facts["worktree"].endswith("demo-x"))

    def test_get_prints_one_bare_fact(self):
        repo = self.repo()
        self.write_file(repo, "## Project\ntrunk: develop\n\n## Heavy runs\npgrep -f \"pytest -m slo[w]\"\n")
        self.assertEqual(self.run_in(repo, "config", "--get", "trunk"), (0, "develop\n", ""))
        self.assertEqual(self.run_in(repo, "config", "--get", "heavy-runs")[1], 'pgrep -f "pytest -m slo[w]"\n')
        self.assertEqual(self.run_in(repo, "config", "--get", "seams"), (0, "", ""))
        code, out, _ = self.run_in(repo, "config", "--get", "worktree", "--slug", "demo")
        self.assertEqual((code, out.strip()), (0, os.path.join(os.path.dirname(repo), "demo-demo")))
        self.assertIn("## Heavy runs", self.run_in(repo, "config")[1])

    def test_scout_section_is_known_and_kept_apart_from_standing_rules(self):
        repo = self.repo()
        self.write_file(repo, "## Standing rules\nrun the suite before READY\n\n"
                              "## Scout\ncheck the job queue for failures\n")
        facts = coord.config(cwd=repo)
        self.assertEqual(facts["warnings"], [])
        self.assertEqual(facts["sections"]["Scout"], "check the job queue for failures")
        self.assertNotIn("job queue", facts["sections"]["Standing rules"])
        self.assertEqual(self.run_in(repo, "config", "--get", "scout"), (0, "check the job queue for failures\n", ""))
        self.assertEqual(self.run_in(repo, "config", "--get", "standing-rules")[1], "run the suite before READY\n")
        self.assertEqual(json.loads(self.run_in(repo, "config", "--json")[1])["sections"]["Scout"],
                         "check the job queue for failures")
        self.assertIn("## Scout", self.run_in(repo, "config")[1])

    def test_get_scout_is_empty_without_the_section(self):
        repo = self.repo()
        self.assertEqual(self.run_in(repo, "config", "--get", "scout"), (0, "", ""))

    def test_get_refuses_unknown_fact_and_worktree_without_slug(self):
        repo = self.repo()
        code, _, err = self.run_in(repo, "config", "--get", "branch")
        self.assertEqual(code, 2)
        self.assertIn("trunk", err)
        code, _, err = self.run_in(repo, "config", "--get", "worktree")
        self.assertEqual(code, 2)
        self.assertIn("--slug", err)

    def test_outside_a_repository(self):
        lone = os.path.join(self.tmp.name, "lone")
        os.makedirs(lone)
        code, _, err = self.run_in(lone, "config")
        self.assertEqual(code, 1)
        self.assertIn("not inside a git repository", err)

    def test_init_file_writes_refuses_and_forces(self):
        repo = self.repo()
        code, out, _ = self.run_in(repo, "init-file", "--trunk", "main", "--worktree-root", "~/trees",
                                   "--at-cut", "uv sync")
        self.assertEqual(code, 0)
        path = os.path.join(repo, ".devmeta", "streams.md")
        with open(path) as f:
            text = f.read()
        self.assertIn("## Project\n\ntrunk: main\nworktree root: ~/trees", text)
        self.assertIn("## At cut\n\nuv sync", text)
        self.assertNotIn("## At landing", text)  # only the sections that have content
        self.assertNotIn("## Resources", text)
        facts = coord.config(cwd=repo)
        self.assertEqual((facts["at_cut"]["value"], facts["warnings"]), ("uv sync", []))

        code, _, err = self.run_in(repo, "init-file", "--trunk", "other")
        self.assertEqual(code, 2)
        self.assertIn("--force", err)
        with open(path) as f:
            self.assertEqual(f.read(), text)

        code, _, _ = self.run_in(repo, "init-file", "--trunk", "other", "--at-landing", "make test",
                                 "--at-landing", "make lint", "--force")
        self.assertEqual(code, 0)
        facts = coord.config(cwd=repo)
        self.assertEqual(facts["trunk"]["value"], "other")
        self.assertEqual(facts["at_landing"]["value"], "make test\nmake lint")
        self.assertEqual(facts["at_cut"]["value"], "")

    def test_init_file_writes_a_home_path_as_tilde(self):
        repo = self.repo()
        home_path = os.path.join(os.path.expanduser("~"), "trees")  # what an unquoted ~/trees becomes
        self.assertEqual(self.run_in(repo, "init-file", "--worktree-root", home_path)[0], 0)
        with open(os.path.join(repo, ".devmeta", "streams.md")) as f:
            self.assertIn("worktree root: ~/trees\n", f.read())
        self.assertEqual(coord.config(cwd=repo)["worktree_root"]["value"], home_path)

    def test_init_file_with_nothing_writes_a_header_only(self):
        repo = self.repo()
        self.assertEqual(self.run_in(repo, "init-file")[0], 0)
        facts = coord.config(cwd=repo)
        self.assertIsNotNone(facts["file"])
        self.assertEqual((facts["trunk"]["value"], facts["warnings"]), ("main", []))


if __name__ == "__main__":
    unittest.main()
