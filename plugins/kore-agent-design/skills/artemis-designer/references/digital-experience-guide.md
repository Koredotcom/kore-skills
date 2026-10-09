# Digital experience guide

Read this reference with [experience-design-guide.md](experience-design-guide.md) when web, mobile, messaging, collaboration, SMS, or email behavior materially affects the design. Create one experience file per distinct interaction model, not automatically per channel. Apply the shared customer-review summary, critical journeys, decisions, and coverage review.

## Required structure

```markdown
<!-- kore-agent-design:digital-experience:v2 -->
# Digital Experience: <Experience Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md.>

## Experience Summary

<Use the shared experience guide. Include material user goals, recommended interaction behavior, and decisions awaiting confirmation.>

## Critical Journeys

<Show material Wave 1 success and recovery journeys using the shared experience guide.>

## Scope and Applicable Channels

<Channels, use cases, waves, authentication context, languages, devices, and exclusions.>

## Interaction and Content Model

<Message length, cards/forms/attachments, navigation, progressive disclosure, citations, accessibility, formatting, and unsupported-content fallback.>

## Session and Asynchronous Behavior

<Session continuity, inactivity, resume, notifications, delayed work, duplicate messages, ordering, and cross-device behavior.>

## Channel Variations

| EXP reference | Channel or condition | Expected behavior | Constraint | Applicable use cases |
|---|---|---|---|---|

## Identity, Privacy, and Confirmation

<Identity signals, reauthentication, sensitive display, confirmation, consent, and shared-device considerations.>

## Handoff and Failure Experience

<Transfer, context package, availability, delivery failure, retry, unavailable features, and recovery.>

## Experience Acceptance Criteria

| ID | Scenario | Given | When | Then | Evidence method |
|---|---|---|---|---|---|

## Experience Decisions

<Use the shared experience guide to define EXP decisions with rationale, evidence and confirmation status.>

## Experience Coverage

<Show functional, technical, and test coverage for critical journeys and EXP decisions without duplicating the use-case SOP.>

## Open Questions

| ID | Question | Affected use cases | Owner or evidence needed | Blocking? |
|---|---|---|---|---|
```

## Category rules

- Group channels only when their interaction and capability constraints are materially the same.
- Design around the user's underlying concern and context, including frustration, bad news, and recovery; avoid generic empathy text or demo-like dialogue scripts.
- Make critical steps, decision points, and outcomes reviewable by the customer without duplicating the functional SOP.
- Define fallback when a card, form, attachment, deep link, notification, or formatting feature is unavailable.
- Treat email and asynchronous messaging differently from a live chat session when timing and ordering matter.
- Trace each `EXP-###` and experience `AC-###` to applicable use cases.
- Keep transport configuration and payload mechanics in technical documents.
