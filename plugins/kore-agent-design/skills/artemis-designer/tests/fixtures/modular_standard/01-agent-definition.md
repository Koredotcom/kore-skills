<!-- kore-agent-design:agent-definition:v2 -->
# Agent Definition: Equipment Request Agent

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-001 |
| Document type | Agent Definition |
| Version | 0.1 |
| Status | In Review |
| Owner | Workplace Operations |
| Wave | All |
| Canonical owner for | Shared agent behavior, BR-001, and NFR-001 |
| Source evidence | Approved equipment-request discovery |
| Last updated | 2026-09-21 |

## Purpose and Business Outcomes

Help authenticated employees request approved equipment and receive a recorded outcome.

All figures below are synthetic fixture assumptions, not observed customer results.

| Business outcome | KPI and measurement window | Baseline | Target | Measurement source | Evidence status | Owner / next action |
|---|---|---|---|---|---|---|
| Employees receive timely equipment decisions | Share of submitted requests with a recorded decision within two working days, measured monthly | 60% in the fictional pre-launch month | Proposed 90% in the first full month after launch | Request-system submission and decision timestamps | Assumption | Workplace Operations / confirm baseline and target before acceptance planning |

## Operating Model and Boundaries

Hybrid: conversation starts a durable approval process.

## Users, Stakeholders, and Authority

Employees request equipment; managers approve; Workplace Operations fulfills requests.

## Shared Behavior

The agent authenticates, confirms consequential submissions, and links users to [UC-001](use-cases/UC-001-equipment-request.md).

## Knowledge and Content

The approved catalog is the source of truth.

## Shared Human Handoff

Support receives failed requests with the request identifier and current state.

## Universal Guardrails and Business Rules

| ID | Rule or guardrail | Applies to | Enforcement or evidence | Status |
|---|---|---|---|---|
| BR-001 | Only an authorized manager may approve | UC-001 | TD-002 | Confirmed |

## Shared Non-Functional Requirements

| ID | Category | Measurable requirement | Applies to | Evidence or owner |
|---|---|---|---|---|
| NFR-001 | Audit | Every decision records actor, outcome, and time | UC-001 | Workplace Operations |

## Shared Assumptions and Open Questions

No blocking shared question remains.
