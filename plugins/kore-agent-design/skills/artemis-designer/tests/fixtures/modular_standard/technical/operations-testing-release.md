<!-- kore-agent-design:operations-testing-release:v2 -->
# Operations, Testing, and Release: Equipment Request Agent

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-008 |
| Document type | Operations, Testing, and Release |
| Version | 0.1 |
| Status | In Review |
| Owner | Delivery Operations |
| Wave | Wave 1 |
| Canonical owner for | NFR-002 and release evidence |
| Source evidence | Operational-readiness review |
| Last updated | 2026-09-21 |

## Service Objectives and Operational Ownership

| ID | Objective or responsibility | Threshold/scope | Owner | Evidence or status |
|---|---|---|---|---|
| NFR-002 | Approval failures alert support | Every terminal technical failure | Support | Confirmed |

## Observability

Trace UC-001 workflow transitions, API-001 outcomes, approval latency, and NFR-001 audit events.

## Support and Runbooks

Support receives request state and correlation identifiers.

## Test Strategy and Traceability

AC-001 and AC-002 cover the functional and voice outcomes; NFR-002 covers failure alerting.

## Wave 1 Verification

Verify FND-001, UC-001, INT-001, API-001, TD-001, TD-002, and business acceptance.

## Release Plan

Wave 1 uses a controlled pilot and explicit go-live approval.

## Rollback and Recovery

Routing can return to the existing process without deleting durable requests.

## Post-Release Validation

Monitor completion, failure, handoff, and approval outcomes.

## Operational Decisions and Open Questions

No blocking operational question remains.
