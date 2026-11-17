<!-- kore-agent-design:index:v2 -->
# Agent Design Index: Equipment Request Agent

## Status Legend

| Term | Plain meaning |
|---|---|
| Confirmed | Supported by supplied evidence or an explicit answer; scope approval is recorded separately. |
| Documented capability | Product documentation or environment evidence supports this capability. |
| Proposed | A recommendation awaiting a decision. |
| Assumption | A working belief that still needs confirmation. |
| TBD | An answer or decision is still needed. |
| Not verifiable | The evidence needed to check this is unavailable. |
| Not applicable | This does not apply, with a stated reason. |

Document status: **Working Draft** means being written; **In Review** means awaiting review; **Approved** means accepted for the recorded scope/version; **Superseded** means replaced. Checklist status: **Pending** means not started; **In progress** means underway; **Blocked** means unable to proceed; **Complete** means finished with evidence; **Deferred** means explicitly moved outside this cycle with a follow-up; **Not applicable** means irrelevant with a reason. These describe different things; a confirmed fact does not approve a whole document.

## Reading Map

Start with the [Executive brief](00-business-brief.md). Business reviewers read the use-case and experience files assigned in the Sign-off Matrix. Technical reviewers read their assigned technical files. The coordinator reconciles the whole package; each reviewer reads only the files they sign.

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
| Last updated | 2026-11-13 |

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
| DOC-009 | [Executive brief](00-business-brief.md) | Executive Brief | 0.1 | In Review | All | Derived summary; owner: Workplace Operations |
| DOC-001 | [Agent Definition](01-agent-definition.md) | Agent Definition | 0.1 | In Review | All | Shared behavior |
| DOC-002 | [Equipment Request](use-cases/UC-001-equipment-request.md) | Use Case | 0.1 | In Review | Wave 1 | UC-001 behavior |
| DOC-003 | [Voice Experience](experience/voice.md) | Voice Experience | 0.1 | In Review | Wave 1 | Voice behavior |
| DOC-004 | [Architecture](technical/architecture.md) | Architecture | 0.1 | In Review | Wave 1 | Architecture decisions |
| DOC-005 | [Connectivity](technical/connectivity-integrations.md) | Connectivity and Integrations | 0.1 | In Review | Wave 1 | Integration design |
| DOC-006 | [Use-Case APIs](technical/use-case-apis.md) | Use-Case APIs | 0.1 | In Review | Wave 1 | API contracts |
| DOC-007 | [Data and Security](technical/data-security.md) | Data and Security | 0.1 | In Review | Wave 1 | Data and authorization |
| DOC-008 | [Operations and Release](technical/operations-testing-release.md) | Operations, Testing, and Release | 0.1 | In Review | Wave 1 | Test and release design |

## Kickoff decisions and customer actions

| Decision or access item | Customer owner | Needed-by date | What it blocks | Status | Canonical evidence / next action |
|---|---|---|---|---|---|
| Provide environment access | Customer platform owner | TBD — agree before setup | Project setup | Pending | FND-001 / confirm access and date |
| Confirm outcome baseline and target | Workplace Operations | TBD — agree before acceptance planning | Acceptance planning | Pending | [Outcome measures](01-agent-definition.md#purpose-and-business-outcomes) / replace synthetic assumptions |

## Sign-off Matrix

Each reviewer reads only the files they sign. The design coordinator reconciles cross-file consistency. All assignments and decisions in this fixture are synthetic; scope approval is not design approval.

| File | Version | Review area | Reviewer / customer role | Status | Decision evidence / date | Next action |
|---|---|---|---|---|---|---|
| [Executive brief](00-business-brief.md) | 0.1 | Business | Workplace Operations | Pending | No design approval yet | Confirm summary after source review |
| [Shared behavior](01-agent-definition.md) | 0.1 | Business | Workplace Operations | Pending | No design approval yet | Review charter and outcome measures |
| [Equipment request](use-cases/UC-001-equipment-request.md) | 0.1 | Business | Workplace Operations | Pending | No design approval yet | Review goal, SOP and both sample conversations |
| [Voice experience](experience/voice.md) | 0.1 | Business | Workplace Operations | Pending | No design approval yet | Review voice behavior |
| [Architecture](technical/architecture.md) | 0.1 | Technical | Technical design owner | Pending | No design approval yet | Review architecture |
| [Connectivity](technical/connectivity-integrations.md) | 0.1 | Technical | Integration owner | Pending | No design approval yet | Review connectivity |
| [API contracts](technical/use-case-apis.md) | 0.1 | Technical | API owner | Pending | No design approval yet | Review contracts |
| [Data and security](technical/data-security.md) | 0.1 | Technical | Security owner | Pending | No design approval yet | Review controls |
| [Operations and release](technical/operations-testing-release.md) | 0.1 | Technical | Operations owner | Pending | No design approval yet | Review acceptance and release |
| [Design index](00-design-index.md) | 0.1 | Coordination | Design coordinator | Pending | No design approval yet | Reconcile scope, assignments and evidence |

## Design Completion Checklist

**Finalization scope:** Wave 1 equipment-request functional, voice and technical design, including shared behavior.

| Task | Stage | Scope | Status | Evidence or rationale | Next action / owner | Updated |
|---|---|---|---|---|---|---|
| Confirm source inventory and scope | Discovery | Scope Baseline | Complete | Synthetic discovery baseline recorded above | None — Design owner | 2026-11-13 |
| Draft executive brief | Draft | [Executive brief](00-business-brief.md) | Complete | Synthetic summary drafted from canonical scope, outcomes and readiness | None — Design owner | 2026-11-16 |
| Resolve kickoff actions | Discovery | Kickoff decisions and customer actions | Pending | Access and outcome confirmation pending | Resolve customer actions — Design owner | 2026-11-16 |
| Draft shared behavior | Draft | [shared behavior](01-agent-definition.md) | Complete | Fixture document version 0.1 drafted | None — Design owner | 2026-11-13 |
| Draft equipment request | Draft | [equipment request](use-cases/UC-001-equipment-request.md) | Complete | Fixture version 0.1 includes both sample conversations | None — Design owner | 2026-11-13 |
| Draft voice experience | Draft | [voice experience](experience/voice.md) | Complete | Fixture document version 0.1 drafted | None — Design owner | 2026-11-13 |
| Draft architecture | Draft | [architecture](technical/architecture.md) | Complete | Fixture document version 0.1 drafted | None — Design owner | 2026-11-13 |
| Draft connectivity | Draft | [connectivity](technical/connectivity-integrations.md) | Complete | Fixture document version 0.1 drafted | None — Design owner | 2026-11-13 |
| Draft API contracts | Draft | [API contracts](technical/use-case-apis.md) | Complete | Fixture document version 0.1 drafted | None — Design owner | 2026-11-13 |
| Draft data and security | Draft | [data and security](technical/data-security.md) | Complete | Fixture document version 0.1 drafted | None — Design owner | 2026-11-13 |
| Draft operations and release | Draft | [operations and release](technical/operations-testing-release.md) | Complete | Fixture document version 0.1 drafted | None — Design owner | 2026-11-13 |
| Check structure | Validation | All registered files v0.1 | Pending | Not yet checked | Run package checker — Designer | 2026-11-13 |
| Review semantics | Validation | All registered files v0.1 | Pending | Not yet reviewed | Review goal tests, metrics, samples, brief and traceability — Design reviewer | 2026-11-13 |
| Confirm design | Approval | All registered files v0.1 | Pending | Scope approval does not approve this design | Collect file-scoped sign-offs in Sign-off Matrix — Design owner | 2026-11-13 |
| Finalize design | Finalization | Wave 1 design package v0.1 | Pending | Awaiting validation and design confirmation | Reconcile finalization gate — Designer | 2026-11-13 |

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

NOT READY for project setup: environment access and design confirmation remain open. Structural traceability is present for the first use case; validation and semantic review are pending. Outcome baseline and target need customer confirmation. Continue assigned file reviews and kickoff actions.
