# Agent definition guide

Read this reference when creating or updating `01-agent-definition.md`. This document owns behavior shared across use cases and modalities.

## Required structure

```markdown
<!-- kore-agent-design:agent-definition:v2 -->
# Agent Definition: <Agent Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md.>

## Purpose and Business Outcomes

<Problem, agent charter, measurable outcomes, and success definition.>

## Operating Model and Boundaries

**Type:** Conversational | Process | Hybrid

<Agent responsibilities; boundaries among conversation, workflow, systems, and humans; work that may outlive a conversation; explicit exclusions.>

## Users, Stakeholders, and Authority

| Role or persona | Needs and responsibilities | Identity source | Access or approval authority |
|---|---|---|---|

## Shared Behavior

<Behavior that applies to multiple use cases: opening, authentication, context handling, clarification, confirmation, fallback, cancellation, status, and completion conventions. Define shared persona and tone boundaries; link to modality-specific realization rather than duplicating it.>

## Knowledge and Content

<Sources, ownership, permissions, freshness, grounding, citations, unsupported-answer behavior, and evaluation expectations.>

## Shared Human Handoff

<Destinations, eligibility, availability, context transferred, unsuccessful-transfer behavior, and return or closure. Distinguish conversational handoff from process approval.>

## Universal Guardrails and Business Rules

| ID | Rule or guardrail | Applies to | Enforcement or evidence | Status |
|---|---|---|---|---|

## Shared Non-Functional Requirements

| ID | Category | Measurable requirement | Applies to | Evidence or owner |
|---|---|---|---|---|

## Shared Assumptions and Open Questions

| ID | Status | Item | Why it matters | Owner or next action |
|---|---|---|---|---|
```

## Category rules

- Put behavior here only when it applies across use cases. Link from a use-case file instead of copying it.
- Keep channel-neutral behavior here. Put modality-specific behavior in the applicable experience document.
- Define how the agent adapts tone to context without generic empathy preambles, false reassurance, or promises beyond its authority. Preserve the user's underlying goal alongside the literal request.
- Define authorization boundaries in business terms; technical enforcement belongs in data/security or architecture.
- Keep use-case sequences, branches, and acceptance criteria in the use-case files.
- Give shared `FR`, `BR`, `NFR`, and `OQ` identifiers stable canonical definitions.
