# Run limits and specialist ownership

The coordinator owns one run plan and ledger. Defaults come from [baseline-slas.json](baseline-slas.json); record user overrides, definitions and target provenance. Read available matching evidence before spending new live test attempts. An offline case is labelled evidence analysis, not a newly executed conversation.

## Allocate before dispatch

Create scenario IDs with expected outcomes and design/checklist links, including passing controls. Explain the short plan to the user and proceed under existing authority; ask only where target, test inputs or effects remain unapproved. Unknown fields do not prevent independent offline work.

Use at most one experience worker and one performance worker. Give each:

- The public Reviewer entrypoint, its specialist reference, investigation/finding contracts and frozen context revision.
- Exact read-only design/source/evidence paths and the source identity, known exclusions and intended channels.
- Assigned scenario IDs, an explicit output directory under its own `reviews/` and `evidence/` subfolders, and no shared-file write access.
- Exact permitted operations/effects, session namespace, allocated attempts/turn cap and the **same absolute deadline**.
- Required return artifacts: checks and outcomes, source/session/turn/trace links, hypotheses/confidence, proposed changes/verification, completed and incomplete attempts, consumed limits and coverage gaps.

Do not give a benchmark worker held-out expected findings or a diagnosis to reproduce. For repair verification, the finding and expected behavior are necessary inputs; keep Developer's claimed success distinct from reviewer evidence.

Only the coordinator updates the ledger and canonical results; workers return their own attempt logs. Preallocate disjoint session/attempt ranges so concurrent workers cannot each spend the total allowance. Example: of 10 conversations, reserve one setup attempt, four performance attempts and five experience attempts. Count setup failures and retries. If setup needs another attempt, subtract it before dispatch. Reallocate only known unspent capacity after reconciling the worker log. An unresponsive worker's reserved attempts remain unavailable until its state is known.

The ledger records run ID, context/snapshot, execution start/deadline, limits, reservations and attempts: attempt/scenario/session/owner, start/end, user turn count, status, effects, evidence links and stop reason. Count each submitted user input as one user turn, with its response/tool activity. Ambiguous submissions count as consumed until reconciled; don't retry unknown consequential outcomes blindly.

## Sessions and timing

Each worker verifies its own tool connection to the confirmed target when tool state is worker-local. Use explicit unique session IDs for every debug call. Persist transcript, source version and trace/tool evidence during execution before worker-local buffers disappear. A coordinator must not assume it can fetch another worker's trace later. Record unavailable telemetry honestly.

Use isolated test identities, records and sessions. Serialize tests sharing state and latency runs that concurrency would distort; analysis of saved evidence may run concurrently. Do not inject failures into an unapproved service or create load tests from a diagnostic allowance. Workers cannot mutate project source, invoke Developer, deploy, share reports or spawn further workers.

Start the execution clock at the first live setup/test attempt, including response waits. The deadline is elapsed wall time, not the sum of worker durations. A paused/interrupted running budget does not restart on resume. Before each input check conversation count, that conversation's turn count and deadline; stop at the first limit. Bound tool waits to the remaining time where supported. At expiry, dispatch no further input, end/cancel supported outstanding test work safely and record any unavoidable overrun. A timed-out or abandoned attempt remains in the ledger.

When a setup defect prevents meaningful testing, report it and continue source/evidence analysis. Tests may adapt within the remaining allowance to distinguish causes; record the reason, new scenario and displaced coverage. Exhaustion ends testing, not reporting. Never create a fresh run just to bypass the cap.

## Integration and fallback

Wait for the specialists' saved artifacts, inspect claims against source/evidence and reconcile overlapping findings. Preserve differing confidence or contrary evidence. The coordinator also reviews design-to-component coverage and shared architecture/routing/security boundaries; specialists do not certify each other's conclusions.

For a substantial combined review, use both specialists when available. With only one worker slot, execute them sequentially. When subagents are unavailable or the task is too small for meaningful delegation, perform both roles sequentially, label that limitation and never claim independent specialist validation. Worker failure should lead to a bounded retry/reassignment within remaining limits or partial coverage, not fabricated completion.
