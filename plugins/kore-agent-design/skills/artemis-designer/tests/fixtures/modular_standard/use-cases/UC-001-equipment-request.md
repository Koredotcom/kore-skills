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

**Business objective:** Give employees a recorded equipment-request outcome, supporting the [business outcome measures](../01-agent-definition.md#purpose-and-business-outcomes).

**Trigger:** An employee asks to request an item from the approved catalog.

**Actors:** Employee, agent, authorized manager, request system and Workplace Operations.

**Preconditions:** The employee is authenticated, the catalog is available and a manager can be assigned. FND-001 is required.

**Completion outcome:** The employee receives a recorded approval or rejection outcome.

**Out of scope:** Purchasing and physical delivery of approved equipment.

## Inputs and Evidence

The item and justification come from the authenticated employee.

## Functional Requirements

| ID | Requirement | Evidence status | Dependencies |
|---|---|---|---|
| FR-001 | Persist the request while approval is pending | Confirmed | NFR-001 |

## Business Rules

The shared authorization rule is [BR-001](../01-agent-definition.md).

## Functional SOP

1. Confirm the employee's identity using the shared authentication behavior.
2. Collect the requested catalog item and justification.
3. Summarize the request and ask the employee to confirm submission.
4. Record the confirmed request and route it to the authorized manager.
5. Preserve the pending request while awaiting the manager's decision.
6. Record and report the approval or rejection to the employee.

## Branches, Exceptions, and Recovery

Approval and rejection are terminal; unavailable systems follow [INT-001](../technical/connectivity-integrations.md) recovery.

## Human Participation

An authorized manager approves or rejects before expiration.

## Sample Conversations

Illustrative voice conversations, not runtime evidence. The later manager decision resumes the pending request; channel behavior is owned by the [voice experience](../experience/voice.md).

### Happy path

| Speaker | Message |
|---|---|
| User | I need to request an ergonomic keyboard. |
| Agent | What is the reason for your request? |
| User | My current keyboard is uncomfortable during long typing sessions. |
| Agent | Submit a request for an ergonomic keyboard for more comfortable typing? |
| User | Yes. |
| Agent | Your request is recorded and waiting for your manager's decision. |
| Manager | I approve the keyboard request. |
| Agent | Your keyboard request has been approved. |

### Failure path

| Speaker | Message |
|---|---|
| User | I want to request a second monitor. |
| Agent | What is the reason for your request? |
| User | I need more screen space when comparing reports. |
| Agent | Submit a request for a second monitor to compare reports? |
| User | Yes. |
| Agent | Your request is recorded and waiting for your manager's decision. |
| Manager | I reject the request because this item is not approved for this role. |
| Agent | Your manager declined the monitor request because it is not approved for your role. No equipment will be ordered from this request. |

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
