# Experience design guide

Read this reference before creating or updating a channel experience document. It defines the shared experience layer; then read the applicable voice or digital guide. The use-case file owns business behavior, the agent definition owns shared behavior, and the experience file owns what users observe in a particular modality.

## Customer-review opening

After document metadata, begin with an approval-ready summary of intended users and situations, experience outcome, material design recommendations, decisions awaiting confirmation, assumptions and exclusions, and affected use cases and waves. Keep it short enough to review without reading technical configuration. Mark recommendations `Proposed` until confirmed; user confirmation of a design choice is not evidence of a customer-approved scope baseline.

## Critical journeys

For each material Wave 1 journey, show the user situation and goal, agent behavior the user will notice, consequential information or action, recovery variation, and linked `UC`, `FR`, `BR`, or `EXP` IDs. Include important failure and handoff paths. Use short illustrative utterances only where wording affects a decision; do not write demo scripts or duplicate the use-case SOP.

| Step | User situation and goal | Observable agent behavior | Critical action or information | Recovery variation | Linked IDs |
|---|---|---|---|---|---|

## Experience decisions

Give each material modality-specific requirement a stable `EXP-###` defined here. Record the recommended behavior, user or business rationale, evidence state, confirmation state and actor/date when known, applicable use cases and requirements, technical dependency if any, and acceptance evidence. Prefer a small decision table so the user can confirm recommendations together or revise specific rows. Propagate a confirmed change to affected use cases, technical files, tests, and the index through normal change control.

Define the identifiers in the `Experience Decisions` table. Other sections reference those IDs without redefining them.

| EXP ID | Recommended behavior | Rationale and evidence state | Confirmation status | Linked IDs and dependency | Acceptance evidence |
|---|---|---|---|---|---|

## Coverage review

Check each critical journey or experience requirement against its functional source, experience treatment, technical dependency, and acceptance or test evidence. A capability need not appear in a scripted showcase; it must be traceable and testable where relevant.

Put this trace in `Experience Coverage`.

| Journey or EXP ID | Functional source | Experience treatment | Technical dependency | Acceptance or test evidence | Coverage status |
|---|---|---|---|---|---|

## Design standard

- Start from users' underlying goals, context, and likely points of uncertainty, not a feature tour or idealized happy path.
- Vary tone and level of detail by situation, while keeping shared persona and business boundaries consistent.
- Define what happens when understanding, an integration, delivery, or a handoff fails. Make the recovery observable and proportionate to consequence.
- Keep design choices distinct from platform configuration. Product-specific settings require current public documentation or supplied environment evidence and belong in the appropriate technical file.
- Avoid claiming universal voice, channel, or accessibility settings. Propose a context-specific design, validate it with representative users and scenarios, and record remaining uncertainty.
