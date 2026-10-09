# Design index guide

Read this reference whenever creating, updating, or reviewing a modular package. The index is the governance record and authoritative source for document status and wave placement.

## Required index structure

Use this structure for `00-design-index.md`:

```markdown
<!-- kore-agent-design:index:v2 -->
# Agent Design Index: <Agent Name>

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-000 |
| Document type | Design Index |
| Version | 0.1 |
| Status | Working Draft |
| Owner | <name or role> |
| Wave | All |
| Canonical owner for | Package governance, document register, wave scope, baselines, and change history |
| Source evidence | <sources> |
| Last updated | <YYYY-MM-DD> |

## Engagement and Design Context

<Business problem, intended outcome, sponsor or decision owner, agent type, target product, and delivery context.>

## Evidence Register

| Evidence ID | Source | Authority or owner | Date/version | Availability | Facts supported |
|---|---|---|---|---|---|

## Scope Baseline

**Baseline status:** Customer approved | Internally approved | Proposed | Not available

**Phase terminology:** <Wave 1, Phase 1, or mapping>

**Target:** <30 working days or supplied target>

<Confirmed scope, exclusions, customer agreement evidence, and any provisional-scope notice.>

## Document Register

| Document ID | Document | Type | Version | Status | Wave | Canonical ownership |
|---|---|---|---|---|---|---|
| DOC-001 | [Agent Definition](01-agent-definition.md) | Agent Definition | 0.1 | Working Draft | All | Shared agent behavior |

## Foundation Register

| ID | Foundation item | Wave | Status | Dependencies | Evidence or owner |
|---|---|---|---|---|---|
| FND-001 | <platform, environment, channel, identity, integration, governance, or operational foundation> | Wave 1 | Proposed | <dependencies> | <evidence> |

## Use-Case Prioritization

| Use case | Value (1–5) | Speed (1–5) | Readiness (1–5) | Score | Selection rationale | Evidence status |
|---|---:|---:|---:|---:|---|---|
| [UC-001](use-cases/UC-001-<slug>.md) | <value> | <speed> | <readiness> | <product> | <reason or override> | <Confirmed, Proposed, or Not verifiable> |

## Wave Plan

| Use case | Wave | Scope status | Foundation dependency | Target outcome | Customer agreement |
|---|---|---|---|---|---|
| [UC-001](use-cases/UC-001-<slug>.md) | Wave 1 | Confirmed | FND-001 | <outcome> | <evidence or Not available> |

## Traceability Summary

| Business outcome or requirement | Canonical design | Technical treatment | Acceptance evidence | Coverage status |
|---|---|---|---|---|

## Experience Decision Summary

| Experience ID | Canonical decision | Confirmation status | Affected use cases or waves | Next action |
|---|---|---|---|---|

<Link only material EXP decisions. The experience file owns their full rationale, evidence, and approval record; update this summary in the same increment as a material decision change.>

## Decisions and Changes

### Confirmed decisions

| Decision | Rationale | Evidence or approver | Date | Affected IDs |
|---|---|---|---|---|

### Change history

| ID | Change | Baseline affected | Affected IDs/documents | Owner | Approval status | Effective version |
|---|---|---|---|---|---|---|

## Risks, Dependencies, and Open Questions

### Risks and dependencies

| Item | Impact | Owner | Due date or trigger | Status |
|---|---|---|---|---|

### Open questions

| ID | Question | Why it matters | Owner or evidence needed | Blocking? | Affected IDs |
|---|---|---|---|---|---|

## Readiness Snapshot

<Current verdict, critical blockers, Wave 1 feasibility, and next review action.>
```

## Wave governance rules

- Use `Wave 1` as the canonical label and record any supplied `Phase 1` terminology as an alias.
- Preserve a customer-approved baseline. Mark proposed changes separately and never rewrite the approved record silently.
- When customer-approved discovery evidence is unavailable, set the baseline to `Proposed`, assign an `OQ-###`, and keep wave assignments provisional.
- Wave 1 includes foundation plus at least one use case. Record Value, Speed, and Readiness scores only when supplied or explicitly confirmed; never invent them.
- Verify score arithmetic deterministically when scores are present. A lower-scoring selection needs a documented reason.
- Use 30 working days as the default Wave 1 planning target unless the evidence establishes another target. Assess feasibility from scope and readiness evidence without inventing an effort estimate.
- Keep later-wave items visible with exclusions and prerequisites so deferred scope cannot disappear.

## Index maintenance rules

- Update the document register whenever a file is added, renamed, superseded, or changes status, version, or wave.
- The index links to every canonical package document. A document absent from the register is outside the governed package.
- Update the traceability summary after material functional or technical changes.
- Keep the experience decision summary synchronized with applicable voice and digital files; do not treat a user's confirmation of design recommendations as customer approval of the scope baseline.
- Record only a concise readiness snapshot; keep detailed findings in `reviews/design-review.md`.
