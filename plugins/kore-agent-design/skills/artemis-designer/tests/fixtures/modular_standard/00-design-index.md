<!-- kore-agent-design:index:v2 -->
# Agent Design Index: Equipment Request Agent

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-000 |
| Document type | Design Index |
| Version | 0.1 |
| Status | In Review |
| Owner | Workplace Operations |
| Wave | All |
| Canonical owner for | Package governance, wave scope, and change history |
| Source evidence | Approved equipment-request discovery |
| Last updated | 2026-09-21 |

## Engagement and Design Context

Design an authenticated equipment-request agent with manager approval.

## Evidence Register

| Evidence ID | Source | Authority or owner | Date/version | Availability | Facts supported |
|---|---|---|---|---|---|
| E-001 | Discovery notes | Workplace Operations | 1.0 | Available | Scope and Wave 1 |

## Scope Baseline

**Baseline status:** Customer approved

**Phase terminology:** Phase 1 is recorded as Wave 1.

**Target:** 30 working days

Wave 1 includes the platform foundation and equipment-request use case.

## Document Register

| Document ID | Document | Type | Version | Status | Wave | Canonical ownership |
|---|---|---|---|---|---|---|
| DOC-001 | [Agent Definition](01-agent-definition.md) | Agent Definition | 0.1 | In Review | All | Shared behavior |
| DOC-002 | [Equipment Request](use-cases/UC-001-equipment-request.md) | Use Case | 0.1 | In Review | Wave 1 | UC-001 behavior |
| DOC-003 | [Voice Experience](experience/voice.md) | Voice Experience | 0.1 | In Review | Wave 1 | Voice behavior |
| DOC-004 | [Architecture](technical/architecture.md) | Architecture | 0.1 | In Review | Wave 1 | Architecture decisions |
| DOC-005 | [Connectivity](technical/connectivity-integrations.md) | Connectivity and Integrations | 0.1 | In Review | Wave 1 | Integration design |
| DOC-006 | [Use-Case APIs](technical/use-case-apis.md) | Use-Case APIs | 0.1 | In Review | Wave 1 | API contracts |
| DOC-007 | [Data and Security](technical/data-security.md) | Data and Security | 0.1 | In Review | Wave 1 | Data and authorization |
| DOC-008 | [Operations and Release](technical/operations-testing-release.md) | Operations, Testing, and Release | 0.1 | In Review | Wave 1 | Test and release design |

## Foundation Register

| ID | Foundation item | Wave | Status | Dependencies | Evidence or owner |
|---|---|---|---|---|---|
| FND-001 | Development, test, and production setup | Wave 1 | Confirmed | Environment access | Platform owner |

## Use-Case Prioritization

| Use case | Value (1–5) | Speed (1–5) | Readiness (1–5) | Score | Selection rationale | Evidence status |
|---|---:|---:|---:|---:|---|---|
| [UC-001](use-cases/UC-001-equipment-request.md) | 5 | 4 | 4 | 80 | Highest confirmed score | Confirmed |

## Wave Plan

| Use case | Wave | Scope status | Foundation dependency | Target outcome | Customer agreement |
|---|---|---|---|---|---|
| [UC-001](use-cases/UC-001-equipment-request.md) | Wave 1 | Confirmed | FND-001 | Recorded request outcome | Discovery approval |

## Traceability Summary

| Business outcome or requirement | Canonical design | Technical treatment | Acceptance evidence | Coverage status |
|---|---|---|---|---|
| UC-001, FR-001, BR-001, NFR-001 | use-cases/UC-001-equipment-request.md | TD-001, INT-001, API-001, TD-002 | AC-001, EXP-001, AC-002, NFR-002 | Complete |

## Decisions and Changes

### Confirmed decisions

| Decision | Rationale | Evidence or approver | Date | Affected IDs |
|---|---|---|---|---|
| TD-001 uses durable workflow state | Approval can outlive the conversation | Architecture review | 2026-09-21 | UC-001, NFR-001 |
| TD-002 enforces least privilege | Requests contain employee data | Security review | 2026-09-21 | BR-001, NFR-001 |

### Change history

| ID | Change | Baseline affected | Affected IDs/documents | Owner | Approval status | Effective version |
|---|---|---|---|---|---|---|

## Risks, Dependencies, and Open Questions

### Risks and dependencies

| Item | Impact | Owner | Due date or trigger | Status |
|---|---|---|---|---|
| FND-001 environment access | Blocks build | Platform owner | Before setup | Confirmed |

### Open questions

| ID | Question | Why it matters | Owner or evidence needed | Blocking? | Affected IDs |
|---|---|---|---|---|---|

## Readiness Snapshot

Wave 1 is in review with complete traceability for the first use case.
