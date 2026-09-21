## Purpose

Get a **gated fix** from a running stream's branch onto `master` so a host can deploy it,
**without landing the stream**. The stream is unfinished and stays alive.

This is not a landing and `land.md` does not apply: its step 2 requires a finished stream with
a `completion.md` and a hand-over. A hotfix has none of those and must not pretend to. The
distinction is the whole of this door — on 2026-09-21 the seat did this operation with no name
for it, noticed mid-merge, and only then discovered the checklist it was half-following did
not cover it.

## When it applies

All four, or it is not a hotfix:

1. **A host needs it.** Not "master should have it eventually" — something is broken or blocked
   on a box until this lands. Anything else waits for the stream's own landing.
2. **The human has said go.** This puts one stream's work in front of every other stream at
   their next sync. It is never the seat's call alone.
3. **The fix is gated on its branch.** Typecheck and the full suite, green, at a named commit,
   reported by the stream. A hotfix is not a reason to skip a gate; it is a reason the gate
   matters more.
4. **The stream is not finished.** If it *is* finished, this is a landing — use `land.md`.

## Step 1 — Measure, do not read

- `git merge-tree --write-tree master <branch>` — refuse a hotfix with conflicts. Resolving a
  side stream's conflicts on its behalf, mid-increment, is not a thing the seat should do.
- The main checkout clean, `git worktree list` reconciled against the table.
- The machine: a merge is not heavy and needs no window, but the **typecheck in step 3** is a
  real run. Under the narrowed rule that is permitted alongside anything but a writing run.

## Step 2 — Say what rides along, before you merge

**A merge is not a cherry-pick.** Everything on that branch lands, not the three files anyone
is thinking about. On 2026-09-21 a three-file fix carried twenty-six: the increment's records,
twelve `.tick/issues/*.json`, two `docs/current/` pages, the todo, the diary — and
`.tick/config.md`, **the shared method contract**, which then faced every stream at its next
sync.

So: list the non-fix files for the human *before* merging, and name anything that changes how
other streams work. If the branch carries something that should not go yet, the answer is not
a cherry-pick — it is that the stream splits it off first, on its own branch, where it belongs.

## Step 3 — Merge, verify, then move the ref

Merge into `master` in a **scratch worktree**, `--no-ff`, then **typecheck the merged tree
before `update-ref`**. Uncached — a cached pass proves nothing about a merge. A clean
`git merge` is not evidence the result compiles: a conflict boundary inside a structure makes
keep-both drop a token while git reports success.

The merge message carries the evidence, because a chat nobody can find is not a record:
- that it is a **partial** land and the stream stays alive;
- the branch commit the gates were green at, with the numbers;
- **the migration answer** (below);
- the non-fix files that rode along.

## The migration question, when a host has content

**Before any deploy to a database holding anything a person wrote**, answer in the merge
message: does this carry a migration? Count them on `master` and on the branch, and diff
`packages/db/migrations`. Then name **which instrument** answered it — this is where a vacuous
pass hides. On 2026-09-21 the worker's boot log (`applied: 0`, migration files present) was the
real evidence and the **web** health check was not, because the standalone web image ships no
migration files and its own comment treats an unavailable comparison as a pass. The worker is
the only process that migrates; web's green proves nothing about the schema.

A hotfix carrying a migration against an unsnapshotted production database is **not** a hotfix
the seat performs. It is a decision for the human, with the count as evidence.

## Step 4 — Hand off the SHA, and nothing else

Tell the stream that owns the host **the commit master ended up on**. Do not tell it the host
is running that commit, and do not check on its behalf: it reads `BUILD_SHA` on the box itself,
**and a disagreement between the two is the finding**. Two instruments beat one assertion, and
the stream that asked for it this way was right — it could not distinguish "the image changed
because the deploy landed" from "the image changed because something recreated it", so it
declined to guess.

Then announce to every other stream that master moved and why — **announce, never merge into
their branches.**

## Step 5 — Say plainly what did not happen

The stream keeps its branch, worktree, port block, row and increment. Its row does **not**
become `landed`. Tell its session in as many words: *master having your commits is not your
increment being landed*, and its real landing will merge the rest.

## Corrections from real runs

- 2026-09-21, first one (09s2-nco's Brave source-cap fix): the operation had no name, so the
  seat reached for `land.md`, whose step 2 demands a finished stream. Writing this file is the
  correction. Everything above is what that landing actually did, except step 2, which is what
  it should have done and did only halfway — the human was told what rode along, but after the
  merge was already prepared rather than before.
