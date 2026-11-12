"""Tests for coord.py: holds and their ends, refusals, OWED/PAID, local time across DST.

    cd scripts && python3 -m unittest -v test_coord

Every test writes into a temporary COORD_DIR, never into a real repository's coord/.
"""
import datetime as dt
import io
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
        self._env = {k: os.environ.get(k) for k in ("COORD_DIR", "COORD_AS", "TZ")}
        os.environ["COORD_DIR"] = self.dir
        os.environ.pop("COORD_AS", None)

    def tearDown(self):
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
        with open(os.path.join(self.dir, coord.LOG), "w") as fh:
            fh.write("2026-01-14 09:00 UTC alpha: HOLD stage: written by hand, no end\n")
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
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = coord.main(list(argv))
        return code, out.getvalue(), err.getvalue()

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


if __name__ == "__main__":
    unittest.main()
