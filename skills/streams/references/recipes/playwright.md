## Recipe: Playwright screenshot tiers as a heavy run

Optional. A project whose heavy run is a Playwright tier with screenshot baselines points its
`## Heavy runs` here. Nothing in the doors reads this file unless the project's file names it.

### What the project's file says

```markdown
## Heavy runs

- Playwright UI tier: `pgrep -f "playwright tes[t]"`; a match is a runner only when it is a
  `node` process under `node_modules`, not a shell. A tier in a container: `docker ps`.
- A reading tier takes no hold; a tier that writes baselines into a shared place does.
- Recipe: references/recipes/playwright.md (the streams skill).
```

`status` prints the HEAVY RUNS line from the pattern; `land` step 1 refuses while it matches;
`land` step 6 runs the tier on the merged tree.

### The update modes — read them before arbitrating between observations

- A bare `--update-snapshots` presets to **`changed`**: it rewrites only snapshots that did
  *not* match, so a within-tolerance stale baseline stays where it is.
- **`=all`** rewrites every snapshot of every executed test whose **bytes** differ, matching
  ones included; byte-identical files are left alone (no write, same mtime). No tolerance
  comparison happens under `all`, so mtime changes if and only if the hash changes.
- **No flag** defaults to **`missing`**: it writes a baseline for any spec lacking one, so a new
  visual test creates its own picture on an ordinary run unless the run excludes it
  (`--grep-invert @visual`, say).
- Under `all` a missing snapshot is written and the test **continues**, so a forced pass writes
  both shots of a test that takes two; on a reading run, a failed first shot aborts the test and
  the second is never compared.

### Redrawing two streams' baselines at a landing

Take either side, merge, then delete the concerned spec's `__screenshots__` and re-run with
`--update-snapshots` (or `=all`) for the specs either side touched, on the merged tree, in one
commit. Under `changed` the delete is load-bearing; under `all` it is ceremony.

### Rules

- A change that **reflows** (adds height) is not small at any page length; a change in place
  vanishes into a full-page tolerance, more so on a long page. Label each change reflowing or
  in-place and predict its baseline before the run.
- A reflowing state whose baseline does **not** move is a finding: the state did not render.
- An unchanged baseline has three meanings — nothing changed, under tolerance, or not in frame
  (an overlay covering it) — and only reading the render tells them apart.
- When one test shoots more than one baseline, force the earlier one first and confirm the test
  runs to completion before reading the later one.
- "The test passed" and "the picture was written" are different facts; `git status` is an
  accurate list of what `all` wrote.
- When a change could have touched a rendered surface, read the render or reason from the
  component, and record the attribution on the tick: a stale-and-green baseline otherwise
  surfaces in somebody else's regeneration and is charged to them.
- Bound workers through what the config reads (an env var), or call `playwright test
  --project=<p> <spec>` directly: a wrapper that forwards `--` literally turns a flag into a
  filename filter.
- Force over the pages that wear a change rather than trusting a census: a `changed` pass leaves
  partial sweeps in place.
- A Playwright run inside a container shows on the host as `root` with an unreadable `cwd`:
  attribute it through `docker ps`, and print `held by <container>`.

### Field notes

- (2026-09-21) a three-sentence caption added 40 px at desktop and 100 px at phone and failed an
  admin page at 0.03–0.05 against a 0.01 cap — the tick had reasoned about its area and forgot
  its height.
- (2026-09-21) one app-bar link changed 27 captures and only the two shortest went red — whether
  a picture notices an in-place change depends on the page's length.
- (2026-09-21) a changed `Select` option on an admin page stayed green under tolerance and the
  tick reported "passed unchanged" — true of the test, false of the page.
- (2026-09-21) a header change left a phone baseline untouched because a chat drawer covered the
  header — not in frame, not under tolerance.
- (2026-09-21) the seat wrote that a forced pass stops at a test's first missing shot; the source
  said it continues — read the source before telling a stream how a mode behaves.
- (2026-09-21) a three-bucket mtime/hash manifest had a bucket that cannot occur under `all` — a
  manifest gives per-file hashes to revert against, not proof a picture was examined.
- (2026-09-21) two forced passes, checked by sha256 rather than exit code: 171 rewritten, 146
  kept with a named cause, 25 reverted, and the verification pass wrote nothing.
- (2026-09-21) a forced pass rewrote twelve-plus files from three earlier partial sweeps — a
  regenerating stream names which rewritten files are its own and which it inherited.
- (2026-09-21) two streams measured `--update-snapshots` from outside and disagreed; it was three
  modes, answered by one `--help`.
- (2026-09-21) a "single test" re-run through a wrapper's literal `--` ran all four projects for
  fifteen minutes.
- (2026-11-04) eight full tiers, two at once: 0 of 246 pictures over tolerance — contention makes
  false failures, not false passes, so a landing's tier takes no machine-wide hold.
