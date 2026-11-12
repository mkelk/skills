# Lean epics: what a run spends, and where the checks pay

2026-11-12. Observations from the fh project's `look` side stream (increment 11s128-kqr, a design
increment: colour tokens, small UI components, one page, a logo, then a frame). Not authoritative: a
proposal for dmtix and the ticks engine, to settle after one more epic gives numbers.

## Where it came from

Morten, mid-run, after E1: *"can we make this increment efficient in tokens and not wasting time on
overdoing testing"*, then: *"are they something that we should consider for general improvement of
dmtix?"*. From E2 on the run went lean (below). This note records what E1 cost, what the checks found,
and which changes look general.

## What E1 cost

E1 was four read-only scouts for planning, one wave of four implementer ticks, a final review, and two
follow-up ticks from the review. Numbers are the harness's per-subagent totals; minutes rounded down.

| Tick | Model | Subagent tokens | Minutes | Result |
|---|---|---|---|---|
| four planning scouts | (default) | 208,970 | <1 each | maps of the code to touch |
| tokens and colour rule | sonnet | 110,860 | 15 | done, but merged red (see below) |
| UI components | sonnet | 106,536 | 21 | done |
| one page (Kurzia's home) | sonnet | 120,239 | 17 | done, unfiled four flaky pictures to redraw them |
| logo drawing | opus | 188,218 | 18 | done |
| final review | opus | 162,758 | 7 | 0 blockers, 4 should-fix |
| review fixes, page | sonnet | 107,995 | 12 | done |
| review fixes, rules | sonnet | 109,615 | 10 | done |
| **total** | | **~1.11M** (implementers and review ~906k) | | |

Every implementer ran the same per-tick gates: typecheck, the tests its change reaches (`--changed`),
the scripts suite, three pin tests by name, the web build, its own UI specs, a redraw of its pictures,
and a planted fault per new test ("watch it fail"). The orchestrator then ran the full suite per wave.

## What the checks actually found

- **The one real break came from the wave gate, not a tick.** A tick added a product colour block;
  `tokens.test.ts` held the old "one look" rule and failed. The tick's `--changed` run never reached it,
  because that test reads `tokens.css` by path, not by import. Every tick-level gate passed; the full
  suite at the wave caught it.
- **The final review found four real issues** no gate could: a rule table naming the wrong colours, six
  avatar colours doubling as chip colours, a greeting that named readers by their email's local part,
  and held or dropped issues counting as new. Each would have reached readers. Best value in the epic.
- **Pictures were redrawn three times.** Two ticks redrew their own; the orchestrator redrew the shared
  style guide after the merge; the fix ticks redrew again. Only the last redraw counted.
- **The planted-fault ritual** found nothing on word tables and class maps; it earned its cost on the
  hash, the clock edges and the host rules.
- **The fixed cost per implementer is large.** Each one reads the brief, the rules, the learnings file
  (16 KB), the project's CLAUDE.md and the code it touches before writing a line. A small tick (a few
  word changes and two tests) still cost ~108k tokens.

## What the run changed from E2 on

1. 2-3 ticks per epic, split by files that do not overlap, not one tick per deliverable.
2. A tick runs typecheck, the tests its change reaches, and the build. No UI specs, no redraws, no pin
   or docs-number runs, planted faults only on real logic.
3. The orchestrator runs the full suite, the scripts suite, diagrams and the changed pages' specs once
   at the epic gate, and redraws the pictures once (or has one cheap agent redraw and flag).
4. Shorter briefs: the task, the gates, the boundaries, the report shape. No look pages unless a human
   must decide.
5. The final review drops to Sonnet when the diff is Sonnet's and the logic is plain; Opus only for
   tricky logic. This note argues against that change (see "Keep").

First E2 data point: a sonnet tick on a lean brief (proxy rewrites, built icons, a share card, a header,
tests) cost 105,755 tokens in 13 minutes, about the same as E1's sonnet ticks. The saving is not in the
tick's own run; it is in fewer ticks, gates run once, and redraws done once. E2's totals come at its close.

## What looks general (proposal)

| Change | Where it would live | Why general |
|---|---|---|
| Two gate tiers: per tick (typecheck, reached tests, build) and per wave or epic (full suite and everything slow) | ticks engine, `references/agent-runner.md` (per-tick verification vs post-wave gate) | The wave gate is where cross-tick breaks show; repeating slow gates per tick buys little. |
| Size ticks against the fixed context cost: split by disjoint files, aim for 2-3 per epic unless the work is large | ticks engine, tick-patterns / Definition of Ready | "Atomic, 1-3 iterations" yields too many ticks when the work shares context. |
| Shared generated files (screenshots, baselines, built assets) are regenerated once, by the integrator, after the merge | ticks engine, "At wave end" guidance | Ticks regenerating shared outputs duplicate work and collide. |
| Planted-fault ("watch it fail") only where the logic can be wrong in a way a test should catch | ticks engine, implementer prompt | It costs a run per test; on data tables it proves nothing. |
| A test that reads a source by path escapes `--changed`; run a package's tests whole after editing a file that tests read by path | project learnings, and a line in the engine's testing guidance | Cheap rule; it was the only break in E1. |
| The project's own gate commands and redraw procedure | the project's `.tick/config.md` `## Testing` | Project-specific; dmtix bootstrap could offer a two-tier Testing skeleton without commands. |

dmtix itself stays a door ("doors, not engines"): the only dmtix-side change would be the bootstrap
template offering an optional two-tier `## Testing` skeleton, with no commands in it.

## Keep

- **The final review at the top model.** E1's review was the cheapest finder of reader-facing bugs. Do
  not lower its tier to save tokens; scope it to the epic's diff.
- **The human gate on taste** (the logo, the colour rules): one look page, through the coordinator.

## Open

- E2's totals vs E1's (tokens per delivered DoD item, minutes, rework found at the gate and the review).
  Settle the proposal after that.
- Whether the learnings file (read in full by every implementer, 16 KB cap) should be split into a short
  always-read part and a looked-up part; it is a fixed cost on every tick.
