# Use-case design guide

Read this reference before creating or updating any file under `use-cases/`. Create one file for every distinct user goal or triggered process outcome.

## What counts as a use case

A use case is one distinct goal that a person contacts the agent solely to resolve. For a process agent, it is one outcome that a trigger event exists solely to achieve.

Test each candidate:

- Would someone call, chat or write in for this alone? If not, it is a step inside another use case.
- Does it end with a result the person sees as done?

For a process agent, apply the same test to the event: does the trigger exist solely for this outcome, and is there an observable completed result for its business owner?

Steps such as authentication, identity checks, address capture or payment capture are not use cases. They belong in shared behavior or inside the parent use case. A step becomes its own use case only when people also contact the agent for it alone, for example "Update my address". Other use cases then reference it.

Name each use case as a verb plus a specific object, in the customer's words. Good: "Check order status", "Reset online banking password", "Dispute a card transaction". Not allowed: "Handle incoming users", "Manage customer queries", "Process requests". Split any label that covers more than one goal.

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

## Sample Conversations

### Happy path

| Speaker | Message |
|---|---|
| User | <request in the customer's words> |
| Agent | <observable response; continue through completion> |

### Failure path

| Speaker | Message |
|---|---|
| User | <request or input> |
| Agent | <material failure and available recovery; continue through a clear outcome> |

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

- Apply the distinct-goal and naming tests before allocating a `UC-###`. Welcome, fallback, reminders, and lifecycle hooks belong in shared behavior or the use case they support.
- Describe business behavior rather than endpoints, payloads, nodes, prompt text, or code.
- Name the condition and resulting behavior for every material branch; avoid a final generic “error handling” step.
- Model every terminal outcome, including success, rejection, cancellation, expiration, transfer, and unrecoverable failure when applicable.
- Treat conversational escalation and process approval as different behaviors.
- Make every `AC-###` observable and trace it to requirements and later to technical tests.
- Every Wave 1 use case needs two concise sample conversations in the tables above: a happy path through the completed outcome and a material failure path through recovery, handoff or a clear terminal result. Mark them illustrative and identify any proposed behavior. They demonstrate the SOP and acceptance criteria; they are not exhaustive demo scripts, production prompts or runtime test evidence. Later-wave skeletons may defer them explicitly.
- For a process-only agent with no conversational interface, use the same two Speaker/Message tables to show the trigger source, agent and receiving system or business owner exchanging events/results. Label them illustrative process exchanges; do not invent a chat interface.
- Link the use case's material experience moments, including failure or handoff, to the applicable `EXP-###` and experience file. The sample conversations stay here; modality rules, detailed journey walkthroughs and their approval records stay in the experience file. Reference shared rules instead of duplicating their definitions.
- A flow diagram is optional. Add one only when many branches make the use case hard to follow; it does not replace the two sample tables.
- Preserve the wave assignment from the index. Propose changes through `CHG-###`; do not alter it only in the use-case file.
