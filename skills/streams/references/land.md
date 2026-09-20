## Status: not a door yet — a checklist

Landings are done by hand against this list until two consecutive landings confirm every
step. Each hand landing corrects this file where it was wrong. Then it becomes the door.

## The checklist

1. **Quiet point.** Refuse unless, on the mainline: no tick in progress (`tk list` shows no
   ●), no `playwright test` or `next dev` process, the checkout clean. Prefer between epics;
   mid-epic is acceptable when the streams share no code file. Tell the mainline's session
   you are about to land and give it a stated window to say STOP; silence is consent.
2. **The stream is done.** Its project tick open, `completion.md` present, its session's
   hand-over received (unticked criteria named, files outside its overview's list, baselines
   regenerated, and its `## At landing` heading).
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
   - **The Active block in `current-increment.md`: always the mainline's, whether or not
     git conflicted** — a side branch cut after the mainline's line last changed merges the
     side's block clean, and a lander that checks only the Streams table misses it.
   - `streams.md`: the stream's row → `landed <sha>`.
5. **`## At landing`.** Execute each instruction under that heading in the stream's overview
   (a row to add to `privacy.ts`, a masthead link plus its tooltip key in the same commit) and
   name each in the merge message. A stream that needs the merge to do something says so
   there, not in a chat.
6. **Gate:** `typecheck`, `test`, `docs:diagrams`, `test scripts`; then claim Playwright in
   `streams.md` (`landing: tier running`), tell every session, run the full UI tier on the
   defaults ungrouped under the memory guard, regenerate any shared-page baseline that moved,
   read the failures — a timing failure on one project that passes alone is not a regression.
7. **Close:** commit the merge (message names the seams and the `## At landing` items), push,
   close the stream's project tick with `--from human` and the human's words, remove its
   worktree and branch (local; delete the remote branch if pushed), release Playwright in
   `streams.md`, and print the message to send the mainline's session (the SHA, what changed
   under it, that the machine is free).
