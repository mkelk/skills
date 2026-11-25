## Purpose

Get a **gated fix** from a running stream's branch onto the trunk (`coord.py config --get
trunk`) so a host can deploy it, **without landing the stream**. The stream is unfinished and
stays alive.

This is not a landing and `land.md` does not apply: its step 2 requires a finished stream with a
`completion.md` and a hand-over. A hotfix has none of those and must not pretend to.
(2026-09-21) the seat did this with no name for it and half-followed a landing checklist that
did not cover it.

**Merge to the trunk first, then deploy from the trunk in the main checkout**, unless the
project's `## At hotfix` says otherwise. Deploying a stream's tree directly is the exception,
only with the human's named reason, and that tree is merged to the trunk straight after.
(2026-09-24) five deploys from a stream's tree, merged after, each left the trunk briefly
behind production.

The project's `## At hotfix` (`coord.py config --get at-hotfix`) names its own verify step, its
schema-change check and its deploy hand-off; follow it where it speaks.

## When it applies

All four, or it is not a hotfix:

1. **A host needs it.** Something is broken or blocked on a box until this lands. Anything else
   waits for the stream's own landing.
2. **The human has said go.** This puts one stream's work in front of every other stream at
   their next sync. It is never the seat's call alone.
3. **The fix is gated on its branch.** The project's checks green at a named commit, reported by
   the stream. A hotfix is a reason the gate matters more.
4. **The stream is not finished.** If it is, this is a landing — use `land.md`.

## Step 1 — Measure, do not read

- `git merge-tree --write-tree "$(coord.py config --get trunk)" <branch>` — refuse a hotfix with
  conflicts. Resolving a stream's conflicts on its behalf, mid-increment, is not the seat's
  to do.
- The main checkout clean, `git worktree list` reconciled against the table.
- The machine: a merge is not heavy, but the verify in step 3 is a real run, permitted alongside
  anything but a writing run on a shared singleton.

## Step 2 — Say what rides along, before you merge

**A merge is not a cherry-pick.** Everything on that branch lands. List the non-fix files for
the human *before* merging, and name anything that changes how other streams work (a shared
method contract, say). If the branch carries something that should not go yet, the stream splits
it off first, on its own branch. (2026-09-21) a three-file fix carried twenty-six, including the
shared method contract.

## Step 3 — Merge, verify, then move the ref

Merge into the trunk in a **scratch worktree**, `--no-ff`, then **verify the merged tree before
`update-ref`**: the project's `## At hotfix` verify, else its typecheck or the cheapest check
that reads every file, uncached — a cached pass proves nothing about a merge, and a clean `git
merge` is not evidence the result builds. Before `update-ref`, **put the trunk's
`.devmeta/current-increment.md` header back to the mainline's**: `git checkout <trunk before> --
.devmeta/current-increment.md`, and say so in the message. (2026-09-24) a stream's header
replaced the trunk's cleanly, with no conflict.

The merge message carries the evidence, because a chat nobody can find is not a record:
- that it is a **partial** land and the stream stays alive;
- the branch commit the gates were green at, with the numbers;
- **the schema answer** (below);
- the non-fix files that rode along.

## The schema question, when a host has content

**Before any deploy to a database holding anything a person wrote**, answer in the merge
message: does this carry a migration? Count them on the trunk and on the branch, and diff the
project's migrations directory. Then name **which instrument** answered — the process that
actually migrates (its boot log), never a health check from a process that does not. An
unavailable comparison that reads as a pass is a vacuous pass. (2026-09-21) a web health check
passed while shipping no migration files; the worker's boot log was the real evidence.

A hotfix carrying a migration against an unsnapshotted production database is **not** one the
seat performs. It is a decision for the human, with the count as evidence.

## Step 4 — Hand off the SHA, and nothing else

The deploy that follows runs as the project's `## At hotfix` says, by default from the trunk in
the main checkout. A production host is owned by nobody but the human's go: there the SHA goes
to the human with the exact deploy command to type.

Tell the stream that owns the host **the commit the trunk ended up on**. Do not tell it the host
is running that commit, and do not check on its behalf: it reads the build id on the box itself,
**and a disagreement between the two is the finding**. Two instruments beat one assertion.

Then announce to every other stream that the trunk moved and why — **announce, never merge into
their branches.** Log the hand-off too (`coord.py log`): a message is gone with its session, a
log line is not.

## Step 5 — Say plainly what did not happen

The stream keeps its branch, worktree, resources, row and increment. Its row does **not** become
`landed`. Tell its session in as many words: *the trunk having your commits is not your increment
being landed*, and its real landing will merge the rest.

## Field notes

- (2026-09-21) the human was told what rode along only after the merge was prepared — list it
  before.
