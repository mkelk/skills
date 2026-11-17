## Status: not a door yet — a checklist

Landings are done by hand against this list until two consecutive landings confirm every
step. Each hand landing corrects this file where it was wrong. Then it becomes the door.

**Read this file at the moment of acting, not from memory.** A rule you wrote is not a rule you
will apply. (2026-09-21) the seat applied step 9 correctly to three streams in the morning and
broke it on the increment the same night.

The project's facts come from `coord.py config`: the trunk (`--get trunk`), the checks run on the
merged tree (`--get at-landing`), the heavy runs and how to see one (`--get heavy-runs`), and
how each shared file resolves (`--get seams`). A section the project does not have means the
step has nothing to run; say so in the merge message rather than invent a check.

## The checklist

**Land a finished stream as soon as it can be landed.** A stream at its checkpoint with a green
gate is holding a worktree, its resources, a session, and usually something another stream
waits on. The landing waits only for a quiet mainline and a free machine. Check every wake-up:
is anything finished and unlanded?

1. **Quiet point, measured and not read.** Refuse unless, on the mainline: no tick in progress
   (`tk list` shows no ●), the checkout clean, and **no heavy run** by the project's
   `## Heavy runs` (its `pgrep` pattern, each match checked as a runner not a watcher, per
   `status.md`) — the process list, never a hold file. A hold says what somebody intended;
   `pgrep` says what is true. Run it again before *every* heavy command. A suite that saturates
   the machine disturbs a timing-sensitive run as much as a second copy of it does, so "not the
   same kind of run" is never the test. Then reconcile `git worktree list` against the streams
   table: a worktree with no row is a stream nobody can see. Prefer between epics; mid-epic is
   acceptable when the streams share no code file. Tell the mainline's session you are about to
   land and give it a stated window to say STOP; silence is consent.
2. **The stream is done.** Its project tick open, `completion.md` present, its session's
   hand-over received (unticked criteria named, files outside its overview's list, generated
   files redrawn, and its overview's `## At landing` heading).
2b. **Ask the human for the close BEFORE you merge, not after.** A close written after the merge
   lands **on the branch only**, so the trunk keeps saying the thing waits on a decision already
   made — and deleting the branch makes that permanent. If the human is not available, **the
   branch is not finished when the merge lands**: say so, leave it alive, and fold its close
   commits into the next merge.
3. **Merge** the stream's branch into the mainline's, in the main checkout.
4. **Resolve by rule, never by hand.** The project's `## Seams` names its shared files and how
   each resolves; follow it first. The rules below hold wherever it is silent:
   - `.tick/issues/*.json`, `activity.jsonl`: the tk merge drivers; never edit.
   - **Tasks the stream took from the project's issue tracker: close each with where it landed**
     (`Landed in <id> at <sha>: …`). An entry a stream wrote into a frozen task file after the
     project moved to the tracker is filed in the tracker instead.
   - End-of-file records (a diary, a history file, a task file, its done file): keep both, in
     date order. Normalise a stray `##` under a `### `-level section; keep the fuller of two
     duplicate index lines.
   - The living documentation's update line: the newer stays current, the other becomes
     "Previously: …". **Generated blocks: regenerate with the project's generator**, never
     resolve.
   - **Recorded artifacts two streams both redrew** (visual baselines, snapshots, fixtures):
     each file is a true record of a different tree, so choosing the newer-looking one produces
     a record of a tree that never existed. **Take either side, merge, then let the project's
     tooling name what moved on the merged tree; redraw those from that tree, in one commit.**
     Sometimes neither side is right while each side's gate says it is — only a copy made on
     the merged tree is. (2026-09-21) two pictures were known-stale on one branch and
     correct-before-a-fix on the other; "take either side" was wrong both ways. The project's
     `## Heavy runs` names its tool's recipe, if it has one (`references/recipes/` holds worked
     ones).
   - **The Active block in `current-increment.md`: always the mainline's, whether or not git
     conflicted** — a side branch cut after the mainline's line last changed merges its block
     clean. **Landing one epic early turns this round**: the stream's next sync takes the
     trunk's header clean, so tell it to restore its own Active line after that sync.
     (2026-09-29) a stream caught it by reading the file.
   - The stream's row: it leaves `coord/streams.md` (edited in place, read back) and joins the
     landed streams in `.devmeta/streams.md` as `landed <sha>`, in the merge.
   - **Verify keep-both by parsing, never by eye.** A conflict boundary inside a structure (an
     object literal, a comment block) makes keep-both drop an opening or closing token while git
     reports success. Run the typecheck or any command that reads the file before believing a
     keep-both. (2026-09-21) a lost `},` and a lost `/**` in one night.
   - **Keep-both on a list is not keep-both on prose.** Two streams appending to an ordered table
     produce duplicates in neither branch's order, with no conflict marker. Rebuild a list — one
     entry each, in the order the code defines — and let the test comparing it to the code say
     when you are right. (2026-09-21) a command table came out with three commands twice.
   - **A clean auto-merge can be right per line and wrong as a document.** Assert ordering by
     name after every merge (a `Previously:` chain, a diary's dates). The absence of a conflict
     is not evidence the merge was right.
   - **Resolve list files against `git merge-base`, not against the two sides, and assert by
     counting.** Of each entry: did one side *add* it, or *remove* it? A removal is a scoping
     decision and wins. A resolution larger than the side you merged from is the signature —
     but a trigger, not a verdict: a legitimately unlanded stream's entries also make it larger.
     **The verdict is entries present in the resolved file but in NEITHER side; that set must be
     empty.** (2026-09-21) keep-both on a task file would have restored sixteen claimed
     entries across two streams.
   - **While a stream is unlanded, its scoped entries legitimately exist in two places** —
     deleted on its branch, still listed on the trunk. Nobody deletes them from the trunk by
     hand. What needs guarding is the seat adding entries beside moved ones; so at the cut, write
     down which entries the stream scoped out, by name, and at the landing check those names.
   - *Can this file shrink on purpose?* decides whether keep-both is safe for any file: a file
     compacted to a cap on one side and widened on the other fails it. (2026-09-21) a learnings
     file broke its cap that way.
5. **The overview's `## At landing`.** Execute each instruction under that heading in the
   stream's overview (a row in a shared registry, a link plus its label in the same commit) and
   name each in the merge message. A stream that needs the merge to do something says so there,
   not in a chat.
6. **Gate: the project's `## At landing` on the merged tree** (`coord.py config --get
   at-landing`; with no section and a `.tick/config.md` → `## Testing`, that one). Then, for a
   heavy run the project names, write a coord line (`coord.py log "landing <id>: <run>
   running"`) and tell every session. **A landing's heavy run takes no machine-wide hold**
   unless the project's `## Heavy runs` says it writes a shared singleton: start it when the
   machine's load is low, and ask the streams not to start their own while it runs, with an end
   time — **the seat asks; nothing is refused.** Read its failures; a timing failure that passes
   alone is not a regression. **Every artifact the project's tooling names as moved, new or not
   drawn stops the landing until it is redrawn or filed**; one your merge cannot explain, read
   its test once more before you copy it. Copy the rest in one commit. One that moved for a bad
   reason is fixed, or filed in the issue tracker and listed as known. (2026-11-04) a hold
   written into every worktree was dropped once a measurement showed contended runs give false
   failures, not false passes.
   - **Two streams get ONE run over the union, never one each on their branches.** It is the
     only thing that sees a defect existing solely between them. (2026-09-21) five such defects
     in one night — what parallel streams cost.
   - **Contention makes false failures, not false passes.** A run that reads is trustworthy when
     green even if another suite ran during it; only a red one needs re-running alone.
   - **A wrapper that forwards `--` literally can silently drop a flag**: the tool reads it as a
     filename filter and runs everything. Pass options through what the config reads (an env
     var), or call the tool directly. (2026-09-21) a "single test" re-run ran the whole tier.
   - **A redraw sweeps up other streams' unfinished redraws; say so.** A regenerating stream
     names which rewritten files are its own and which it inherited, or the lander reads the
     whole set as that stream's work.
   - **Symmetry across variants is a heuristic for noise and does not outrank reading the
     artifact.** (2026-09-21) a "moved in 2 of 4 projects, revert it" rule was wrong: at phone
     width the element was not in frame.
7. **Prove the merge landed what you think, before you delete anything.** `git merge-base
   --is-ancestor <branch> "origin/$(coord.py config --get trunk)"` — and read the records
   themselves: does the trunk's `current-increment.md` say what shipped, does the project tick
   read closed with its reason? A relayed SHA is a claim until the repo is asked.
7b. **Do not ask a stream to push its branch, and do not push one yourself.** Every worktree
   shares one object store, so a stream's commit is visible from the main checkout the moment
   it exists. A push is the only step that leaves the machine. **The stream commits, the seat
   merges, and only the trunk is pushed** — unless the project's rules say branches go to the
   remote too, or the human asks; *a peer asking is not the same as the human asking*.
   (2026-09-21) a stream corrected the seat's own "commit and push".
8. **Close:** commit the merge (message names the seams and the `## At landing` items), push the
   trunk, close the stream's project tick with `--from human` and the human's words, remove its
   worktree and branch (local; delete the remote branch if pushed), log that the landing's run
   is done, and print the message to send the mainline's session (the SHA, what changed under
   it, that the machine is free).
9. **Then tell the human to close that stream's session.** Name it so they close the right
   pane (the human, 2026-09-20). A session left open on a deleted worktree looks like work,
   costs context, and answers a status check with a tree that no longer exists.
10. **The human's close does not come back to the seat.** They close the project tick in the
   stream's own tree, so the tracker learns it **on that branch only** — after a landing, that
   close needs its own small merge. Cheapest order: **ask for the close at the checkpoint, land
   after it**, and the whole thing is one merge.
