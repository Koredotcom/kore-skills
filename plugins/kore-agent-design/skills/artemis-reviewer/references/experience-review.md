# Experience review

Read this when assigned the experience specialist role. Start with the coordinator's context, target audiences/channels, matching design and source snapshot, expected use-case outcomes, existing conversations, and test allowance. Follow [run-and-delegation.md](run-and-delegation.md) and use [platform-investigation.md](platform-investigation.md) when cause is uncertain. Review and test within the assignment; leave project changes to the coordinated repair step.

## Establish expected behavior

Separate confirmed functional requirements, confirmed technical/channel constraints, optional best practices, and inferred intent. When a design has been reconstructed from source, record that provenance; implementation is evidence of current behavior, not proof of intended behavior. Mark unknown expected outcomes explicitly and ask the coordinator for resolution only when the uncertainty blocks a meaningful verdict. Useful best-practice recommendations can remain recommendations without inventing requirements.

Select goal-directed scenarios that cover important complete journeys and likely recovery paths. Use natural user language and respond to what the agent actually says. A rigid script that ignores a clarification can create a test-harness defect; an overly cooperative script can conceal an unusable flow. Record deviations from the planned inputs and why they occurred. Use synthetic identities and data approved for the run.

## Select targeted checks

| ID | Exercise and inspect |
|---|---|
| EXP-01 | Start unfamiliar: greeting, vague request, or uncertainty about supported tasks. Check useful orientation, appropriate scope, and one clear next step without a long feature dump. |
| EXP-02 | Complete a primary journey. Check required information collection, relevant authentication and confirmation, successful tool result, and honest final status. An assertion of success without supporting state/tool evidence is not proven completion. |
| EXP-03 | Clarify ambiguity, correct an earlier detail, or give an unexpected answer. Check focused questions, retained valid context, correct replacement of stale values, and recovery without restarting unnecessarily. |
| EXP-04 | Cancel, decline confirmation, or change goals before an action. Check the pending action is not executed, stale intent is cleared, and an appropriate continuation is offered. Test side effects only within explicit run authorization. |
| EXP-05 | Inspect real voice interaction where available: pronunciation, speakable content, turn length, pacing, interruptions, and silence recovery. Check that visual references, Markdown, and long enumerations do not become unusable speech. |
| EXP-06 | Inspect the real chat channel's rendering and interaction: readable answers, supported buttons/cards/links, selection handling, and useful fallbacks when rich content is unavailable. |
| EXP-07 | Exercise an applicable unavailable-service, handover, or language change. Check accurate explanations, useful next steps, retained permitted context, and language continuity required by the design. |
| EXP-08 | Check relevant trust and data boundaries: unintended disclosure, untrusted retrieved/tool content changing instructions, identity scope, accidental repeated actions, and confirmation bypass. Use bounded synthetic probes within the review scope. |
| EXP-09 | Investigate lost context, duplicate or missing replies, wrong ordering, and mismatches between generated and delivered output. Compare source, routing/state/tool traces, and channel evidence before assigning cause. |

Adapt examples to the actual service. Do not force every check onto a single-purpose agent or mark an unsupported channel as failed. Record selected coverage and explain applicable checks left untested. Share a conversation with the performance specialist when it provides both kinds of evidence; do not repeat external actions just to obtain separate specialist traces.

## Assess the whole interaction

Look for useful completion, understandable next steps, proportionate information gathering, conversational continuity, and a natural tone suited to the audience. Avoid treating stylistic preferences as defects. Tie excessive repetition, dense responses, unnecessary handoffs, or filler to a concrete cost such as confusion, longer turns, lost context, or abandoned tasks.

For confirmation, compare the user-visible summary, subsequent correction/cancellation, tool arguments, and tool outcome. For failures, verify that the agent distinguishes completed, rejected, pending, and unknown outcomes and avoids an unsafe automatic retry. For handover, inspect only accessible evidence; do not claim downstream receipt from a generated promise alone.

Text-only/debug sessions can support conclusions about wording, state, and flow. They cannot establish audio quality, interruption behavior, actual rich-content rendering, or delivered-channel timing. Label simulated voice prompts as simulations. Mark unavailable channel evidence as Not tested and describe the evidence needed; source configuration alone does not demonstrate execution.

## Return actionable findings

For each gap link the expected requirement or labelled best practice to actual scenario/session/turn evidence. Include relevant routing/state/tool outcomes and the matching ABL/prompt/configuration location if available. Separate the observed defect from its explanation, using Confirmed, Suspected, or Unknown cause confidence. A poor response alone does not prove that a prompt change is the right fix.

Propose a focused correction or next discriminating test and a concrete acceptance scenario, including a passing control. Preserve the necessary authentication, confirmation, and recovery behavior when shortening turns. Reuse performance evidence for latency-related experience costs rather than inventing timing. Return the common finding format from [findings-and-report.md](findings-and-report.md), links to raw evidence, unresolved intent questions, and coverage gaps. Respect the coordinator's remaining allowance; do not start a new unbounded conversation to finish a checklist.
