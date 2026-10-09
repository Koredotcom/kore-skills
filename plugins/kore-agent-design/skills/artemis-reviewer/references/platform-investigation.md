# Platform and runtime investigation

Use this shared method when performance or experience evidence has multiple plausible explanations. It is part of both specialist assignments, not an automatic third worker. The coordinator retains the test budget, shared state, and repair authority defined in [run-and-delegation.md](run-and-delegation.md).

## Keep observation separate from attribution

Begin with the observed mismatch and the expected behavior's source. Check that design, export/source snapshot, active project, session, and channel belong to the same version and environment. If they do not match, resolve or report that limitation before claiming a source defect. Preserve the original evidence; a successful retry does not erase an intermittent failure.

Consider the plausible boundaries without assuming which is responsible:

| Boundary | Evidence that may distinguish it |
|---|---|
| Project logic/configuration | Agent instructions, ABL control flow, state scope, tool schema/mapping, routing criteria, channel settings, and the actual values/events that exercised them. |
| Platform runtime/channel | Correct configuration alongside contradictory runtime events, duplicated work, lost state, buffering, or generated-versus-delivered differences. |
| Provider/integration | Request/response boundaries, provider timing/errors, tool responses, retries, and outcome reconciliation. |
| Test tooling/telemetry | Harness inputs, simulated channel behavior, missing events, clock skew, logging gaps, source selection, and measurement definitions. |
| Documentation/version mismatch | Capability availability, documented semantics, release applicability, and reproducible behavior differing from the stated contract. |

Consult available current platform documentation through the installed Arch tooling or another supported public documentation source. Read the relevant section, not only a search snippet. Record the source URL or tool/document identifier, retrieval date, and known version applicability. If docs or connector access are unavailable, preserve the question and state the limitation; do not invent platform syntax, APIs, source files, or product guarantees. Runtime behavior and documentation can each be wrong or incomplete.

## Choose the smallest discriminating test

State competing explanations and what observation would support or weaken each. Prefer a comparison using existing equivalent passing and failing sessions. If another test is needed, vary one material factor under comparable project/runtime conditions: for example a fresh versus continued session, an approved known response versus an approved failure fixture, or an observed channel delivery event versus a server completion event. Record unavoidable differences instead of claiming a controlled experiment.

Use only coordinator-assigned remaining conversations, turns, wall time, and external-action permissions. Proposed source/configuration changes go through the authorized repair workflow; review authority alone does not permit changing the system to investigate it. Do not independently replay a potentially completed business action when its outcome is unknown. Ask the coordinator to reconcile that outcome before any retry.

Record each adaptive test's hypothesis, expected distinguishing evidence, cost, result, and any displaced coverage. Stop once the smallest useful test resolves the question or the allowance is exhausted. For intermittent behavior, report observed failures over attempts under specified conditions and keep passing controls. Do not label one unexplained trace a confirmed platform defect or treat one successful retry as proof of a fix.

## Package a useful investigation lead

Return the same finding schema used in [findings-and-report.md](findings-and-report.md), including:

- Expected and actual behavior, with a confirmed requirement or labelled inference and the relevant documentation reference.
- Project/source identity, known runtime/channel/provider versions, minimal reproduction inputs, session/turn/trace or channel evidence, and observed frequency.
- Suspected boundary, supporting and conflicting evidence, cause confidence, and viable alternatives. Cite accessible configuration/source locations; use a named runtime boundary when implementation source is unavailable.
- The next test or logs needed, who could obtain that evidence by capability rather than an assumed employee role, and a bounded workaround if justified.
- Verification conditions and a passing control. State workaround tradeoffs, including latency, user friction, security, and task correctness.

Use Confirmed only when evidence directly establishes the claimed cause; use Suspected for a supported but unproven explanation and Unknown when the evidence cannot distinguish causes. A confirmed observation may still have an unknown cause. Keep unresolved leads in the report, linked across later runs. Do not lower acceptance targets, rewrite intended behavior, or conceal failed attempts to make a suspected defect disappear.
