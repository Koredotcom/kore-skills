# Artemis Designer forward-test scenarios

Run substantial revisions in a clean task with the repository-source or freshly installed skill. Judge observable decisions and generated artifacts, not exact wording.

## Scenario 1: idea without discovery material

Prompt:

> Use `$artemis-designer` to help me design an authenticated employee HR policy assistant. I have only the idea so far.

Expected behavior:

- Asks for discovery or equivalent evidence and a working folder before writing files.
- Continues without discovery, gives the provisional-scope notice once, and does not imply customer approval.
- Requests relevant source material first, extracts answers already supplied, and groups remaining material questions into manageable batches without a total cap.
- Distinguishes customer facts requiring evidence from design choices it can recommend for confirmation.
- Creates the index before category documents once a working folder and enough coherent design context are available.
- Uses the modular package and marks unresolved wave placement `Proposed`.

## Scenario 2: customer-approved Wave 1 input

Prompt:

> Use `$artemis-designer` to turn this discovery package into a design. It contains agreed foundation scope, Value/Speed/Readiness scores, one selected Phase 1 use case, later phases, and a 30-working-day target. Write to the supplied output folder.

Expected behavior:

- Preserves the approved scope baseline, maps Phase 1 to Wave 1, and records evidence in the index.
- Writes and validates the minimum governed package before expanding into experience and technical categories.
- Creates foundation and prioritization registers without inventing scores or effort.
- Designs at least the selected use case and assesses whether access, dependencies, architecture, integrations, and data support the target.
- Records proposed scope changes separately rather than rewriting the approved baseline.

## Scenario 3: bulk multi-use-case requirements

Prompt:

> Use `$artemis-designer` on this large requirements package with six use cases, voice and web, and several integrations.

Expected behavior:

- Establishes source inventory, index, identifier allocation, wave baseline, and document map before parallel work.
- When subagents are available, delegates only independent use cases or categories with bounded source evidence and identifiers.
- Keeps index, agent definition, wave scope, shared identifiers, reconciliation, and final validation under one coordinator.
- Produces the same governed package serially when subagents are unavailable.

## Scenario 4: enterprise voice experience

Prompt:

> Add voice to the approved design for the Wave 1 use case.

Expected behavior:

- Reads the general, index, use-case, and voice references.
- Reads the shared experience reference and covers target-listener voice/accent rationale, speech rate, pronunciation, telephony context, turn-taking, silence, barge-in, recognition repair, confirmation, sensitive values, latency, transfer, disconnect, accessibility, and rendered-audio tests.
- Produces a concise customer-review summary, critical journey with recovery, and evidence-labelled recommendations the user can confirm or alter.
- Does not inherit a demo speech provider, adapter, preset, or numeric threshold.
- Traces `EXP-###` and voice acceptance criteria to the applicable use case.
- Updates the index and affected technical/testing documents without duplicating functional behavior.

## Scenario 5: controlled scope change

Prompt:

> Move UC-003 into Wave 1 and update the design.

Expected behavior:

- Preserves the approved baseline and records a `CHG-###` with rationale, status, owner, affected IDs/documents, and effective version.
- Reviews foundation, dependencies, integrations, APIs, experience, tests, and 30-working-day feasibility.
- Updates wave placement only through the index, then reconciles affected metadata and links.
- Does not report readiness while a material feasibility or approval blocker remains.

## Scenario 6: free-form or legacy review

Prompt:

> Review these existing functional and technical designs. Do not rewrite them yet.

Expected behavior:

- Judges facts across the full artifact set rather than penalizing different headings.
- Uses legacy structural checks only as advisory evidence.
- Reports semantic gaps, traceability, drift, and readiness with exact actions.
- Migrates to the modular package only when requested.

## Scenario 7: explicitly authorized setup

Prompt:

> The reviewed Wave 1 design is ready. Start project setup for the first approved use case in my confirmed development workspace.

Expected behavior:

- Reuses confirmed scope and environment, discovers the platform project-builder contract, and builds only the approved slice.
- Verifies unknown outcomes before retrying and reads back created resources where supported.
- Reports implemented scope and remaining gaps.
- Falls back to an implementation handoff when project-building tools are unavailable.

## Scenario 8: sparse voice evidence with batch confirmation

Prompt:

> Design a voice agent for appointment changes. I can provide our agreed discovery scope, call recordings, brand voice guide, and contact-center architecture. Ask me what you need; you may recommend the accent, speaking pace, and repair behavior.

For repeatable evaluation, supply the fictional [voice appointment discovery fixture](fixtures/voice_appointment_discovery.md) as the agreed-scope brief; no call recordings or architecture need be supplied initially.

Expected behavior:

- Requests the available sources and a working folder; reads the sources before asking questions they answer.
- Asks focused follow-ups for target callers, locales, consequential policies, and constraints still missing after source review; does not enforce a five-question total limit or run a low-value questionnaire.
- Recommends voice character, accent, pace by content type, pronunciation handling, turn-taking, and recovery with evidence states and listening-test needs.
- Accepts “approve these recommendations except make the rate slower for confirmation numbers,” updates the linked experience, architecture, tests, and index, and does not treat this as customer approval of an unsupported scope baseline.

## Scenario 9: implicit project-planning discovery

Run each prompt in a fresh session where the updated skill is available, without explicitly mentioning the skill:

> Help me plan a Kore.ai Artemis project and create its functional design.

> Create the technical design for this Kore.ai Agent Platform project from these requirements.

> Design the voice and web experiences and use cases for our Kore.ai agent.

Expected behavior:

- Selects Artemis Designer and loads its instructions before authoring the design.
- Requests missing relevant evidence and destination, then creates the governed multi-file package and active checklist.
- Does not create or modify a platform project from design-only authorization.

Negative controls: “Plan a kitchen renovation” should not select Designer; “Implement this approved Kore.ai design” belongs to Developer; “Test this deployed agent's conversation performance” belongs to Reviewer. Record actual selection behavior; matching metadata alone does not establish success.

## Scenario 10: persistent checklist through resume and finalization

Use the synthetic modular fixture as an existing design in a temporary working folder. Prompt:

> Continue this design, validate the functional, voice and technical documents, and prepare it for finalization. Use the existing index. I have not approved the design yet.

Expected behavior:

- Reads the saved checklist and current files, preserves completed drafting evidence and separate canonical documents, and resumes pending validation instead of restarting discovery.
- Records actual structural and semantic review evidence independently. Leaves unresolved confirmation work open and does not mark finalization complete merely because checks pass.
- Updates task dates, evidence, next actions/owners and the readiness snapshot before handing back.

Follow up with confirmation of the reviewed version, then a change to voice interruption behavior:

- Applies confirmation only to its actual scope/version, reconciles the finalization gate, and records the resulting state without requiring repeated approval of unchanged decisions.
- On the subsequent behavior change, reopens affected drafting, validation, approval and finalization work; preserves prior evidence in change history and identifies dependent technical/test updates.
- Never copies complete SOPs or technical specifications into the checklist.

## Scenario 11: bounded design and older inputs

Prompt:

> Update only the functional design in this older modular package. Technical design is a later deliverable; do not mark it implementation-ready.

Expected behavior:

- Adds an evidence-based checklist if absent and states functional-only finalization scope.
- Tracks every identified use case separately, preserves later-wave skeletons, and records excluded/deferred work with rationale and ownership.
- Does not invent previous validation or approval evidence or silently mark the entire design complete.
- For a separate review-only legacy input, reports tracking gaps without rewriting or forcing migration.

## Scenario 12: business kickoff and distinct goals

Prompt:

> Design a voice and web agent for our fictional shop. The first release should check order status and update a delivery address before dispatch. Our notes list authentication, identity checks, address capture, payment capture and “Manage customer queries” as additional use cases. We have no measured baseline or agreed access dates yet. Write a functional design to the supplied temporary folder for business kickoff; technical design comes later.

Expected behavior:

- Applies both distinct-goal tests, treats authentication/identity/capture as shared or parent steps, distinguishes standalone “Update delivery address”, and splits or rejects the generic label. Does not add payment processing to scope merely because a capture step appeared in notes.
- Presents a one-page executive brief first with no IDs, summarizing the problem, metrics, Wave 1 scope, exclusions, top risks and an evidence-based verdict.
- Preserves separate index, agent definition, use-case and voice/web experience files. Each Wave 1 use case has happy and failure samples consistent with its SOP and experience decisions; diagrams appear only if many branches warrant one.
- Records baseline, target and source per business outcome, using owned TBD gaps and proposed targets instead of invented measurements. Records customer decisions/access, owners, needed-by dates and blocked work without guessing missing facts.
- Places a plain status legend at the top of the index. Assigns business sign-off to use-case/experience files and tracks technical sign-off as outside this cycle until technical files exist. Each reviewer reads only assigned files; the coordinator reconciles all files.
- Maintains brief, samples, kickoff actions, validation and file-scoped sign-off tasks through completion of the bounded functional draft. Does not call the whole implementation design approved or ready to build.

## Scenario 13: process-only outcome and review findings

Prompt:

> Review a fictional process-agent design triggered by a missed shipment milestone. It should notify the shipment owner after checking carrier status. The design calls its use cases “Receive event”, “Authenticate carrier”, “Process requests” and “Notify shipment owner”. Its single sample is a customer chat even though there is no chat interface. Report findings without changing the source files.

Expected behavior:

- Applies the sole-purpose-trigger/completed-outcome test, flags subprocesses and generic labels, and identifies the distinct business outcome without inventing additional goals.
- Flags the absent happy/failure event-result exchanges and invented conversational interface. Recommends Speaker/Message tables with real event sources and receiving participants.
- Reviews metric evidence, brief readability, kickoff blockers and file-scoped sign-off coverage as substantive findings; does not rewrite the input or infer approvals.

These scenarios are behavioral evaluation recipes. Record an actual run separately; their presence does not establish model behavior.
