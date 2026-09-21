## Status: not a door yet — a checklist

Landings are done by hand against this list until two consecutive landings confirm every
step. Each hand landing corrects this file where it was wrong. Then it becomes the door.

**Read this file at the moment of acting, not from memory.** On 2026-09-21 the seat applied
step 9 correctly to three streams in the morning and broke it on the increment the same
night; the same day an implementer contradicted a learnings rule written three paragraphs
above its own entry. **A rule you wrote is not a rule you will apply.** (inc-08, 2026-09-21.)

## The checklist

**Land a finished stream as soon as it can be landed.** A stream at its checkpoint with a
green gate is not "done later" — it is holding a worktree, a port block, a session, and
usually something another stream is waiting on. The landing waits only for a quiet mainline
and a free machine, never for the end of an evening. Check every wake-up: is anything
finished and unlanded?

1. **Quiet point, measured and not read.** Refuse unless, on the mainline: no tick in progress
   (`tk list` shows no ●), the checkout clean, and **`pgrep -f "playwright tes[t]"` empty** —
   the process list, never a hold file. A hold says what somebody intended; `pgrep` says what
   is true. Run it again before *every* heavy command, not once per landing: **a full Vitest
   suite poisons a screenshot run exactly as well as a second browser does**, so "not a
   browser" is never the test. Then reconcile `git worktree list` against the streams table:
   **a worktree with no row is a stream nobody can see**, and handing the machine away against
   a table that cannot mention it is how two runs collide. Prefer between epics; mid-epic is
   acceptable when the streams share no code file. Tell the mainline's session you are about
   to land and give it a stated window to say STOP; silence is consent.
2. **The stream is done.** Its project tick open, `completion.md` present, its session's
   hand-over received (unticked criteria named, files outside its overview's list, baselines
   regenerated, and its `## At landing` heading).
2b. **Ask the human for the close BEFORE you merge, not after.** This is step 9 promoted,
   because the seat broke it on the increment itself after applying it correctly to three
   streams the same morning. A close written after the merge lands **on the branch only**, so
   the trunk keeps saying the thing is still waiting on a decision that was already made — and
   a lander who then deletes the branch makes that permanent and invisible. If the human is
   available, get the close first and the whole thing is one merge. If they are not, **the
   branch is not finished when the merge lands**: say so out loud, leave it alive, and fold
   its close commits into the next merge.
3. **Merge** the stream's branch into the mainline's, in the main checkout.
4. **Resolve by rule, never by hand:**
   - `.tick/issues/*.json`, `activity.jsonl`: the tk merge drivers; never edit.
   - `docs/diary.md`, `todo/todo.md`, `.devmeta/project-history.md`, `todo/todo.done.md`:
     keep both, in date order. Watch for a `##` heading under `## Details` (streams write
     them) and normalise to `###`; watch for a duplicate index line (both streams wrote the
     same entry) and keep the fuller.
   - `docs/current/_overview.md`'s update line: the newer stays current, the other becomes
     "Previously: …". `README.md` and `_overview.md` numbers blocks: **regenerate with
     `fp docs:numbers`**, never resolve.
   - PNG baselines: take the side stream's, then regenerate from the full run in step 6.
     **This is where two streams' regenerations actually collide — not in the window.**
     Baselines are per-branch files, so two streams regenerating the same shared page are
     each correct on their own tree and neither can overwrite the other; the collision is an
     add/add conflict that surfaces only when the **second** of them lands. So the seat does
     not need to order two regeneration windows to protect a shared page, and saying it will
     is a false comfort. What the second lander needs is the resolution: **take either side,
     merge, then delete that spec's `__screenshots__` and re-run `test:ui:update` for the
     specs concerned.** The tempting move — resolve by choosing the newer-looking file —
     **produces a picture of a page that never existed**, because each file is a true picture
     of a different tree. **The mode decides whether you must delete
     first** (resolved 2026-09-21 by reading `playwright --help`, then sharpened by reading
     `expect.js`: **`all` compares BYTES, not tolerance** — `~12556`,
     `if (!compareBuffersOrStrings(received, expected)) return helper.handleMatching();` — so
     under `all` **the delete is ceremony**, because a stale-under-tolerance file has different
     bytes and is rewritten anyway. It is load-bearing under `changed`, which takes the
     tolerance path and leaves a within-tolerance stale file in place. *The step was right for
     the wrong mode.* That also dissolves the last of the earlier contradiction: both
     observations were simply true of `all`). `fp test:ui:update` passes a **bare**
     `--update-snapshots`, which presets to **`changed`** — it rewrites only snapshots that
     did *not* match, so a within-tolerance stale baseline is left exactly where it is, and
     the delete is load-bearing. **`=all`** rewrites every snapshot of every executed test,
     matching ones included, so there the delete is harmless ceremony. And **no flag at all
     defaults to `missing`**, which silently writes a baseline for any spec that has none —
     so a new `@visual` test creates its own picture on an ordinary run unless the run is
     `--grep-invert @visual`.
   - **The Active block in `current-increment.md`: always the mainline's, whether or not
     git conflicted** — a side branch cut after the mainline's line last changed merges the
     side's block clean, and a lander that checks only the Streams table misses it.
   - `streams.md`: the stream's row → `landed <sha>`.
   - **Verify keep-both by parsing, never by eye.** A conflict boundary that falls inside a
     structure — an object literal, a comment block — makes keep-both drop the opening or
     closing token, and git reports the merge as successful. Seen twice in one night: a lost
     `},` in `scripts/fp.ts`, and a lost `/**` in `config.ts` that stopped the file parsing.
     Run `typecheck` or any command that reads the file before believing a keep-both.
   - **Keep-both on a list is not keep-both on prose.** Two streams appending to an ordered
     table produce duplicate rows in neither branch's order, which no conflict marker shows:
     `config-reference.md`'s command table came out with three commands listed twice. For a
     list, rebuild it — one entry each, in the order the code defines — and let the test that
     compares it to the code tell you when you are right.
   - **A clean auto-merge can be right per line and wrong as a document.** Ordered prose is
     where this bites: git answers "which line is current" and never "what order does the
     history read in". Assert the ordering by name after every merge — `_overview.md`'s
     `Previously:` chain, the diary's dates — rather than waiting for a conflict marker.
5. **`## At landing`.** Execute each instruction under that heading in the stream's overview
   (a row to add to `privacy.ts`, a masthead link plus its tooltip key in the same commit) and
   name each in the merge message. A stream that needs the merge to do something says so
   there, not in a chat.
6. **Gate:** `typecheck`, `test`, `docs:diagrams`, `test scripts`; then claim Playwright in
   `streams.md` (`landing: tier running`), **write `.ui-hold` into every live worktree root
   and every tick worktree, not only the mainline's** — a hold in the holder's own tree is a
   message addressed to whoever already knows to look — tell every session, run the full UI
   tier, regenerate any shared-page baseline that moved, read the failures. A timing failure
   on one project that passes alone is not a regression.
   - **`fp test:ui -- --flag` silently does nothing.** The `--` is forwarded literally and
     Playwright reads the flag as a *filename filter*, so the flag is dropped and the whole
     tier runs. A "single test" re-run spent fifteen minutes running all four projects before
     anyone noticed. Bound workers with **`UI_WORKERS=<n> pnpm fp test:ui`** (the config reads
     that env var), or call `pnpm exec playwright test --project=<p> <spec>` directly.
   - **Two streams get ONE tier over the union, never one each on their branches.** That run
     is the only thing that can see a defect existing solely between them, and in one night
     five such defects appeared — a command table disagreeing with the CLI, a page pushed past
     its line cap because one stream trimmed to just under while the trunk grew beneath it.
     Five in a night is not bad luck; it is what parallel streams cost.
   - **Contention makes false failures, not false passes.** A tier that *reads* baselines is
     trustworthy when green even if another suite ran during it; only a red one in that window
     needs re-running alone. A tier that *writes* baselines is the opposite — a contended
     regeneration cannot certify itself, and the cure is a forced pass on a quiet machine then
     a cold read-back with no `--update-snapshots`.
7. **Prove the merge landed what you think, before you delete anything.**
   `git merge-base --is-ancestor <branch> origin/master` — and read the records themselves,
   not the merge's exit code: does the trunk's `current-increment.md` say what shipped, does
   the project tick read closed with its reason? A SHA someone relayed to you is still a
   claim until the repo is asked. Deleting a branch whose records never reached the trunk
   makes a stale claim permanent, on the trunk, about the thing you just shipped.
8. **Close:** commit the merge (message names the seams and the `## At landing` items), push,
   close the stream's project tick with `--from human` and the human's words, remove its
   worktree and branch (local; delete the remote branch if pushed), release Playwright in
   `streams.md`, and print the message to send the mainline's session (the SHA, what changed
   under it, that the machine is free).
9. **Then tell the human to close that stream's session.** Integrate, delete, and *say so* —
   name the session so they close the right pane (Morten, 2026-09-20). A session left open on
   a deleted worktree is a pane that looks like work, costs context, and will answer a status
   check with a tree that no longer exists.
10. **The human's close does not come back to the seat.** They close the project tick in the
   stream's own tree, so the tracker learns it **on that branch only** — if the stream landed
   before they closed it, that close needs its own small merge or the mainline's tracker still
   reads the gate as open. Cheapest order when the human is available: **ask for the close at
   the checkpoint, land after it**, and the whole thing is one merge.
