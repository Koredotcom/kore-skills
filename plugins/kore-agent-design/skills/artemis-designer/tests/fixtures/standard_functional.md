<!-- kore-agent-design-template:v1 -->
# Agent Functional Design (SOP): Equipment Request Agent

**Document type:** Functional
**Status:** In Review
**Companion technical design:** standard_technical.md

## Document Control

Owned by Workplace Operations; version 0.2.

## Agent Purpose and Business Outcome

Enable employees to submit equipment requests and see a recorded outcome.

## Agent Type and Operating Model

Hybrid: conversation starts a process that may wait for manager approval.

## Users, Stakeholders, and Roles

Employees request equipment; managers approve; Workplace Operations fulfills it.

## Scope

Standard laptop and accessory requests are in scope. Purchasing is out of scope.

## Channels, Languages, and Experience Constraints

English web chat with authenticated employee identity.

## Assumptions and Dependencies

The employee directory and request system are available.

## User Goals and Use-Case Inventory

UC-001 covers submitting a request.

## Functional SOPs

### UC-001 — Submit Equipment Request

The agent collects an item and justification, creates the request, waits for approval, and reports the result. FR-001 requires a durable request. BR-001 requires approval. AC-001 verifies approval and rejection paths.

## Long-Running Workflows, Human Tasks, and Approvals

The request ID correlates the approval task. Managers can approve or reject before the deadline; the process resumes and records the decision.

## Knowledge and Content Requirements

The approved equipment catalog is owned by Workplace Operations.

## Functional Integration Requirements

INT-001 creates and updates the request in the request system.

## Human Handoff and Escalation

Support receives failed requests with the request ID and current state.

## Guardrails, Privacy, and Compliance

Only the employee and authorized approver can view the request.

## Non-Functional Requirements

NFR-001 requires an auditable decision history.

## Success Measures and Acceptance Criteria

AC-001 passes when approval and rejection each produce the correct recorded outcome.

## Risks, Decisions, and Open Questions

The catalog owner and approval policy are confirmed; no blocking question remains.
