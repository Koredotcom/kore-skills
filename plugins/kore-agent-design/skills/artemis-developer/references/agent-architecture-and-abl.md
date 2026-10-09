# Agent allocation and native control

Read before choosing responsibilities, execution modes, routing or ABL control. Names and available constructs vary by platform version: verify mappings before authoring executable source.

## Choose the smallest effective graph

Allocate agents around coherent responsibilities, context and tool permissions. Multiple use cases can share an agent when their state and policy boundaries fit. A separate agent or nested orchestration layer needs a functional reason; every hop can add latency and context-loss risk that must be tested.

For predictable transactions, prefer hybrid execution where the target supports the required behavior: explicit control for steps, guards, state and consequential actions, with model assistance for language/interpretation. Preserve correction, cancel and recovery throughout the flow. Do not confuse determinism with forcing users through redundant questions.

Use reasoning where variable interpretation, synthesis or adaptive planning adds value. Bound the task, evidence sources, tools, permissions, stopping conditions and completion contract. Do not delegate backend ownership or authorization decisions to free-form model judgment. A reasoning step inside a larger workflow is an option to evaluate; full reasoning for every transaction is not a default.

Select routing/orchestration separately from execution mode. Compare available Router/Supervisor or equivalent patterns against selection, multi-agent coordination, aggregation and return requirements. Verify the platform's actual semantics; names alone do not establish which pattern preserves follow-up control.

## Specify every handoff

For each edge in the brief's graph, define the user's goal, already captured typed fields and their provenance, identity context, allowed action, child result/error schema, return owner and terminal-state behavior. Share only needed state. Test a supplied first-turn request, correction after routing, child refusal/failure and a second unrelated request after completion.

Prefer native ABL for supported state transitions, validation, branches, ordered action orchestration and confirmation. Read the relevant construct documentation before selecting expression/condition syntax. Check evaluation ordering explicitly: a condition depending on a tool result must consume the completed current call's result, not an empty or stale value. Use separate supported control steps where required by the runtime.

**Example:** a repair-request journey has known intake, confirmation, submission and result states; a hybrid owner is a strong candidate. A policy explanation may need a bounded reasoning role grounded in approved sources. The specific choice and any expected speed advantage remain proposals until confirmed and measured.

Verify routing with actual session state/traces and outcomes, not only graph shape or compiler acceptance. Preserve separate functional requirements and technical allocation when the graph changes.
