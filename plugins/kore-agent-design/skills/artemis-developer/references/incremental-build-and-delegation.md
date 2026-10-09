# Incremental build, checkpoints and delegation

Read before scaffolding, selecting a slice, delegating or resuming. Work in the supplied/confirmed project workspace; never use the installed skill or overwrite source exports.

## Working artifacts

Use existing equivalent records when present. Otherwise keep:

```text
BUILD_CONTEXT.md
architecture-brief.md
blueprint.md
BUILD_REGISTER.md
project/baseline/<snapshot-id>/
project/working/<run-id>/
runs/<run-id>/plan.md
runs/<run-id>/evidence/
runs/<run-id>/results.md
```

The brief owns the confirmed direction; the blueprint owns dependency/order, shared interfaces, state ownership and implementation allocation. The register tracks `UC ID | dependencies | owner | state | source links | acceptance evidence | blocker/next action` and run history. Use Planned, Scaffolded, Implementing, Validated, Blocked or Deferred; keep test/channel limits explicit even when a slice is Validated for its stated checks.

Do not pre-create empty run histories or every future file. Establish the map, then create supported artifacts as work reaches them. Allocate stable resource names/IDs without inventing platform-generated identifiers.

## Expand complete paths

After architecture confirmation, establish the minimum shared foundation and explicit placeholders. Keep unfinished routes inactive; if partial platform packages are unsupported, keep scaffolds local. Empty schemas, fake API successes and a compiling skeleton are not completed functionality.

Implement the first use case through success, correction/cancel, failure and confirmation. Stabilize its shared contracts before widening parallel construction of dependent cases. Validate and save a snapshot/diff after each coherent increment; run relevant regression checks whenever shared routing/state/tools change. Continue ready authorized scope without requiring approval for each slice.

A blocked external dependency blocks only its dependent tasks. Preserve the blocker, completed work and next discriminating action, then continue independent tasks. If repeated attempts produce no new evidence, stop that retry cycle instead of repeatedly issuing the same action. Never retry an ambiguous external write until its outcome is reconciled.

## Resume

Checkpoint the run/UC state, source and design hashes, live source version if known, completed tests, consumed limits, pending operation/session IDs, unresolved outcomes, changed contracts and next action. On resume compare the checkpoint with current target/source/design; reconcile drift before writing. Preserve earlier evidence and run IDs; distinguish resuming a run from starting a successor. Do not replay completed mutations or reset consumed limits.

## Parallel work that earns its overhead

Use subagents for at least two substantial independent tasks with stable inputs and disjoint output ownership. Good candidates include separate modules after contracts stabilize, isolated channel adaptations or independent contract tests. Small changes and shared routing/state decisions usually stay with the coordinator.

Default to at most two workers, subject to available slots. Increase only for a clear recorded benefit and true independence. Do not launch one worker per use case or permit recursive worker delegation by default.

Each assignment includes the relevant design/IDs, baseline, confirmed decisions, applicable references, allowed paths/isolated copy, task scope, acceptance criteria, API effects and allocated test/time allowance. Workers return files/diffs, checks and evidence, assumptions, blockers and any requested shared-contract change. They do not edit shared contracts, the blueprint/register or the live project.

The coordinator reviews contributions, integrates one bounded increment at a time, reconciles contracts and runs affected regressions. Serialize platform writes, conflicting backend mutations and latency tests whose measurements concurrency would distort. Give workers separate sessions/data when tests are permitted. Where tool connections/traces are worker-local, require workers to persist evidence before completion. All workers consume one shared budget, not separate copies of the allowance.

If a worker fails or delegation is unhelpful, preserve its useful artifacts, explicitly reassign ownership and continue sequentially. Delegation never creates additional authority.
