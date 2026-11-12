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
   - **Tasks the stream took from the project's issue tracker: close each with where it
     landed** (`Landed in <id> at <sha>: …` as the closing comment). A project that moved its
     tasks from a file to the tracker freezes the file; an entry a stream wrote there after the
     move is resolved by filing it in the tracker instead (2026-09-23).
   - `docs/diary.md`, the todo file (`todo.md`), `.devmeta/project-history.md`, `todo.done.md`:
     keep both, in date order. Watch for a `##` heading under `## Details` (streams write
     them) and normalise to `###`; watch for a duplicate index line (both streams wrote the
     same entry) and keep the fuller.
   - The living documentation's `_overview.md` update line: the newer stays current, the
     other becomes "Previously: …". Generated blocks (the `README.md` and `_overview.md`
     numbers blocks, say): **regenerate them with the project's generator**, never resolve.
   - PNG baselines: take the side stream's, then let step 6's check name what moved.
     **This is where two streams' regenerations actually collide.**
     Baselines are per-branch files, so two streams redrawing the same shared page are
     each correct on their own tree and neither can overwrite the other; the collision is an
     add/add conflict that surfaces only when the **second** of them lands. No machine-wide
     window protects a shared page, and none is asked for. What the second lander needs is the
     resolution: **take either side, merge, and let the project's visual-baseline tooling name
     the pictures that moved on the merged tree; redraw those, from that tree, in one commit**
     (with Playwright alone: delete that spec's `__screenshots__` and re-run with
     `--update-snapshots` for the specs concerned). The tempting move — resolve by choosing the newer-looking file —
     **produces a picture of a page that never existed**, because each file is a true picture
     of a different tree.
     **And sometimes neither side is right, while each side's own gate says it is.** Measured
     2026-09-21: `issues.png` and `chat.png` were **known-stale** on one branch — a
     `mask`→`hide` change altered the render's shape and the baselines passed unregenerated
     anyway — and on the other branch they were **correct-for-3900-pre-fix**, recorded before
     that change existed and from a different port block. At the merge, *"take either side"*
     is wrong in **both** directions, and no per-branch gate can see it: each one is green
     against its own tree. **The only correct copy is one made on the merged tree**, which is
     why the wave-end rule exists — run the tier, or at minimum every spec either side
     touched, on the merged tree **before** committing the resolution. A stale-and-green that
     survives both gates is the one class of baseline fault that only the merge can catch. **The mode decides whether you must delete
     first** (resolved 2026-09-21 by reading `playwright --help`, then sharpened by reading
     `expect.js`: **`all` compares BYTES, not tolerance** — `~12556`,
     `if (!compareBuffersOrStrings(received, expected)) return helper.handleMatching();` — so
     under `all` **the delete is ceremony**, because a stale-under-tolerance file has different
     bytes and is rewritten anyway. It is load-bearing under `changed`, which takes the
     tolerance path and leaves a within-tolerance stale file in place. *The step was right for
     the wrong mode.* That also dissolves the last of the earlier contradiction: both
     observations were simply true of `all`). The project's update script passed a **bare**
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
     **Landing one epic early turns this round on the stream.** After the seat keeps master's
     line in an epic landing, the merge base holds the stream's line and only master's side
     changed it, so the stream's next sync takes master's header clean, with no conflict.
     Tell the stream to restore its own Active line after that sync (2026-09-29; the stream
     caught it by reading the file).
   - The stream's row: it leaves `<git common dir>/coord/streams.md` (edited in place, read
     back) and joins the landed streams in `.devmeta/streams.md` as `landed <sha>`, in the
     merge.
   - **Verify keep-both by parsing, never by eye.** A conflict boundary that falls inside a
     structure — an object literal, a comment block — makes keep-both drop the opening or
     closing token, and git reports the merge as successful. Seen twice in one night: a lost
     `},` in the project's CLI script, and a lost `/**` in `config.ts` that stopped the file parsing.
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
     **The absence of a conflict is not evidence the merge was right** — and the two files
     that prove it are the two every landing touches. `current-increment.md`'s header: both
     sides legitimately edit it, git takes one, and the result is wrong with nothing to warn
     you (which is why the Active-block rule above says *always the mainline's, whether or not
     git conflicted*). And the todo file: when a stream scopes an entry it **deletes** that
     entry on its branch, master never saw the delete, so at the merge **a scoping decision
     and an untouched line are indistinguishable** — keep-both silently returns claimed work
     to the trunk. On 2026-09-21 that would have restored **sixteen** entries across two
     streams, and the rule for that file is literally *keep both*.
     **So resolve list files against `git merge-base`, not against the two sides, and assert
     the result by counting.** Ask of each entry: did one side *add* it, or did one side
     *remove* it? A removal is a scoping decision and it wins. Then check the arithmetic: the
     base had 106 entries, the resolution 94, master 95. **A resolution larger than the side
     you merged from is the signature** — it is the cheapest check there is, it needs no diff
     reading, and it catches the one fault a per-branch gate can never see.
     **But the count is a trigger to investigate, not a verdict.** A larger count is also what
     a legitimately unlanded stream looks like: 09s4-hos resolved to 96 against master's 95 and
     the difference was exactly the entries its own cut had moved into its overview, which
     master still carries because that increment has not landed yet. One-home-per-task working,
     not keep-both leaking — and *both* produce a bigger number. **The verdict is the direct
     test: entries present in the resolved file but in NEITHER side. That set must be empty.**
     Anything in it was resurrected by the merge and belongs to nobody. Run the count first
     because it is free, then answer it with that check rather than with an explanation.
     **And say this out loud at the cut, because two streams misread it as a violation on one
     day: while a stream is unlanded, its scoped entries legitimately exist in TWO places** —
     deleted on its branch and present in its overview, still listed on master because master
     has not received the delete yet. That is not the one-home rule breaking; it is branch
     divergence, and it resolves itself at landing. **Nobody should delete the entry from
     master by hand.** Doing so would make the trunk wrong if the stream never lands, and it
     takes the delete out of the merge that is supposed to carry it.
     **What actually needs guarding is the seat's own habit of adding entries to master all
     day, beside entries streams have already moved.** An adjacent addition turns a clean
     one-sided delete into a conflict, and the obvious resolution of that conflict restores
     the moved entry. So at the cut, **write down which entries the stream scoped out, by
     name**, where the lander will read it — and at the landing, check those names against the
     resolved file rather than hoping the merge was clean. The entries at risk are known in
     advance; nothing about this has to be discovered at merge time. The same question
     — *can this file shrink on purpose?* — is what tells you whether keep-both is safe for any
     file at all: `.tick/learnings.md` fails it too, because one side had compacted to its cap
     while the other widened entries in place, and keep-both breaks the cap the compaction
     existed to hold.
5. **`## At landing`.** Execute each instruction under that heading in the stream's overview
   (a row to add to a shared registry file, a navigation link plus its label key in the same
   commit) and
   name each in the merge message. A stream that needs the merge to do something says so
   there, not in a chat.
6. **Gate:** the project's wave gate on the merged tree (typecheck, the full suite, its docs
   and scripts checks); then write a coord line
   saying the landing's UI tier is running (`scripts/coord.py log "landing <id>: full UI tier
   running"`) and tell every session. **A landing's tier takes no machine-wide hold**
   (2026-11-04): no hold file, no window. Start it only when the machine's load is low, and
   ask the streams not to start new full tiers while it runs, with an end time on the
   request: **the seat asks; nothing is refused.** Run the full read-only tier on the merged
   tree with the project's visual-baseline tooling, keeping what it drew. Read its failures; a
   timing failure on one project that passes alone is not a regression. Then look at **every
   picture the check names** — moved, not drawn, new: **a named picture stops the landing
   until it is redrawn or filed.** A picture your merge cannot explain: read its spec once
   more before you copy it; if it goes back, leave it. Copy the rest from the renders in one
   commit. If any was over the tolerance the tier was red, so read it once more; if any was
   new, read it once more too (a new picture stops its test); otherwise, no second run. A
   picture that moved for a bad reason is fixed, or filed in the issue tracker and listed as
   known.
   (Until 2026-11-04 the landing claimed the tier and **wrote `.ui-hold` into every live
   worktree root and every tick worktree, not only the mainline's** — a hold in the holder's
   own tree is a message addressed to whoever already knows to look. The measurement under
   *Contention* below took the reason for a hold away.)
   - **A wrapper that forwards `--` literally silently drops the flag.** `<wrapper> test:ui --
     --flag` reached Playwright with the `--` intact, and Playwright read the flag as a
     *filename filter*, so the flag was dropped and the whole tier ran. A "single test" re-run
     spent fifteen minutes running all four projects before anyone noticed. Bound workers
     through what the config reads (an env var such as `UI_WORKERS=<n>`), or call
     `playwright test --project=<p> <spec>` directly.
   - **Two streams get ONE tier over the union, never one each on their branches.** That run
     is the only thing that can see a defect existing solely between them, and in one night
     five such defects appeared — a command table disagreeing with the CLI, a page pushed past
     its line cap because one stream trimmed to just under while the trunk grew beneath it.
     Five in a night is not bad luck; it is what parallel streams cost.
   - **Contention makes false failures, not false passes.** A tier that *reads* baselines is
     trustworthy when green even if another suite ran during it; only a red one in that window
     needs re-running alone. A tier that *writes* is the same (measured 2026-11-04, eight full
     tiers, two at once: 0 of 246 pictures over the tolerance), and a redraw is still looked at
     and followed by a read. This replaced the rule that a contended regeneration cannot
     certify itself, whose cure was a forced pass on a quiet machine then a cold read-back
     with no `--update-snapshots`.
   - **History, not the procedure (2026-11-04: the landing check and copying from its renders
     replace the forced pass).** **Measured end-to-end 2026-09-21 (09s4-hos), so this
     supersedes the reasoning above rather than sitting beside it.** Two forced passes, 804
     passed / 12 skipped / 0 failed, verified by **sha256 rather than exit code**: 171 rewritten, 146 kept with a named cause,
     25 reverted, and the verification pass wrote nothing — every kept file had the same hash
     afterwards and every reverted file was still byte-identical to HEAD.
     - **Under `all` the delete is ceremony, confirmed.** Three files that had **passed a
       reading gate an hour earlier** were rewritten anyway (`admin-routing.png`,
       `issues.png`, `chat.png`, every project) while four untouched pages came back with the
       **same sha256 and the same mtime**. 169 of 340 left alone. So a forced pass is not
       "rewrite everything": it is a byte comparison, and byte-drift is invisible to the
       tolerance gate that passed an hour before.
     - **A forced pass DOES write both shots of an ordered pair.** Proven with an isolated
       two-snapshot test, first file deleted and second stale: *A snapshot doesn't exist …
       writing actual* → *… is not the same, writing actual* → `✓ 1 passed`, both on disk, and
       all 20 multi-screenshot executions ran to completion. **So the ordered-pair rule
       protects the VERIFICATION run, not the regeneration** — which is the opposite of how
       this door described it.
   - **Expect a forced pass to sweep up other streams' unfinished regenerations, and say so.**
     The same run rewrote **twelve-plus** files belonging to nobody currently running: tick
     `jky` added `Sources` to the admin sidebar on 2026-09-20 and left **eight** admin
     baselines unregenerated (every link below it shifted one 28px row; the files were still
     dated 2026-09-19 while `admin.spec.ts`'s own had been refreshed — **a partial sweep, which
     is the `changed`-mode signature exactly**); a tick's masthead sweep missed
     one image baseline ×4; another tick's credit line left three. **Three separate partial
     sweeps outstanding on master simultaneously.** Two consequences: **force over the pages
     that wear a change rather than trusting a census** — a `changed` pass would have left all
     three — and **a regenerating stream must name which rewritten files are its own and which
     it inherited**, or the lander reads the whole set as that stream's work.
   - **Symmetry across projects is a heuristic for noise and does not outrank reading the
     render.** A rule saying *a baseline that moved in only 2 of 4 projects is scatter, revert
     it* was overruled correctly: at 390px those pages are captured with a drawer over the
     masthead, so the element was **not in frame at all**. Desktop-only movement was the true
     answer. Read the render before applying any symmetry rule.
7. **Prove the merge landed what you think, before you delete anything.**
   `git merge-base --is-ancestor <branch> origin/master` — and read the records themselves,
   not the merge's exit code: does the trunk's `current-increment.md` say what shipped, does
   the project tick read closed with its reason? A SHA someone relayed to you is still a
   claim until the repo is asked. Deleting a branch whose records never reached the trunk
   makes a stale claim permanent, on the trunk, about the thing you just shipped.
7b. **Do not ask a stream to push its branch, and do not push one yourself.** Corrected by
   a stream on 2026-09-21, against this seat's own instruction. **Every worktree on the machine
   shares one object store**, so a stream's commit is visible from the main checkout the
   moment it exists — `git log <branch>` resolves, and the merge works — with nothing reaching
   GitHub. A push is the only step in a landing that **leaves the machine**, it is
   outward-facing, and it is not reversible the way a local commit is. `origin` carries
   `master`; increment branches on it are not the convention. So "commit and push" is a reflex
   sentence with one step too many in it: **the stream commits, the seat merges, and only
   `master` is pushed.** If the branch is genuinely wanted on origin, that is the human's call
   and not a seat's — *a peer asking is not the same as Morten asking*, which is the stream's
   phrase and the right test.
8. **Close:** commit the merge (message names the seams and the `## At landing` items), push
   **master**,
   close the stream's project tick with `--from human` and the human's words, remove its
   worktree and branch (local; delete the remote branch if pushed), write the coord line that
   the landing's tier is done, and print the message to send the mainline's session (the SHA, what changed
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
