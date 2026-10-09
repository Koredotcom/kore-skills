# Use-case design guide

Read this reference before creating or updating any file under `use-cases/`. Create one file for every distinct business outcome.

## Required structure

```markdown
<!-- kore-agent-design:use-case:v2 -->
# UC-### — <Use Case Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md. Set Wave to the index assignment.>

## Outcome and Scope

**Business objective:** <objective>

**Trigger:** <user request or event>

**Actors:** <users, systems, agent, and human roles>

**Preconditions:** <required state>

**Completion outcome:** <observable terminal result>

**Out of scope:** <explicit exclusions>

## Inputs and Evidence

| Input | Source | Required? | Validation | Correction or fallback |
|---|---|---|---|---|

## Functional Requirements

| ID | Requirement | Evidence status | Dependencies |
|---|---|---|---|

## Business Rules

| ID | Rule | Condition | Result | Evidence status |
|---|---|---|---|---|

## Functional SOP

1. <business-level actor or agent action>

## Branches, Exceptions, and Recovery

| Condition or failure | Behavior | Destination or terminal state | User communication | Recovery owner |
|---|---|---|---|---|

## Human Participation

<Handoff, approval, task assignment, authorization, evidence shown, decision outcomes, or Not applicable.>

## Long-Running Behavior

<Correlation identity, persisted state, waits, resumption, duplicate events, deadlines, reminders, cancellation, recovery, audit, and terminal states; or Not applicable.>

## Integration and API Needs

| Business action | System | Data exchanged | INT/API references | Failure expectation |
|---|---|---|---|---|

## Experience Applicability

| Modality or channel | Experience references | Critical moment or variation |
|---|---|---|

## Acceptance Criteria

| ID | Given | When | Then | Evidence method |
|---|---|---|---|---|

## Risks, Dependencies, and Open Questions

| ID or item | Status | Impact | Owner or next action | Blocking? |
|---|---|---|---|---|
```

## Category rules

- Give each distinct business outcome its own `UC-###` file. Welcome, fallback, reminders, and lifecycle hooks belong in shared behavior or the use case they support.
- Describe business behavior rather than endpoints, payloads, nodes, prompt text, or code.
- Name the condition and resulting behavior for every material branch; avoid a final generic “error handling” step.
- Model every terminal outcome, including success, rejection, cancellation, expiration, transfer, and unrecoverable failure when applicable.
- Treat conversational escalation and process approval as different behaviors.
- Make every `AC-###` observable and trace it to requirements and later to technical tests.
- Link the use case's material experience moments, including failure or handoff, to the applicable `EXP-###` and experience file. Keep observable modality behavior and journey walkthroughs in that file rather than copying them here.
- Preserve the wave assignment from the index. Propose changes through `CHG-###`; do not alter it only in the use-case file.
