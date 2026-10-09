<!-- kore-agent-design:use-case:v2 -->
# UC-001 — Submit Equipment Request

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-002 |
| Document type | Use Case |
| Version | 0.1 |
| Status | In Review |
| Owner | Workplace Operations |
| Wave | Wave 1 |
| Canonical owner for | UC-001, FR-001, and AC-001 |
| Source evidence | Approved equipment-request discovery |
| Last updated | 2026-09-21 |

## Outcome and Scope

The employee receives a recorded approval or rejection outcome. FND-001 is required.

## Inputs and Evidence

The item and justification come from the authenticated employee.

## Functional Requirements

| ID | Requirement | Evidence status | Dependencies |
|---|---|---|---|
| FR-001 | Persist the request while approval is pending | Confirmed | NFR-001 |

## Business Rules

The shared authorization rule is [BR-001](../01-agent-definition.md).

## Functional SOP

1. Confirm the employee, collect the item and justification, invoke [API-001](../technical/use-case-apis.md), wait for the authorized decision, and report the outcome.

## Branches, Exceptions, and Recovery

Approval and rejection are terminal; unavailable systems follow [INT-001](../technical/connectivity-integrations.md) recovery.

## Human Participation

An authorized manager approves or rejects before expiration.

## Long-Running Behavior

The request persists and resumes from the correlated approval event under TD-001.

## Integration and API Needs

INT-001 and API-001 create and update the request.

## Experience Applicability

Voice behavior follows [EXP-001](../experience/voice.md).

## Acceptance Criteria

| ID | Given | When | Then | Evidence method |
|---|---|---|---|---|
| AC-001 | A valid request | The manager approves or rejects | The correct outcome is recorded and reported | End-to-end test |

## Risks, Dependencies, and Open Questions

Environment access under FND-001 is required before setup.
