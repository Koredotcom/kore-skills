<!-- kore-agent-design:use-case-apis:v2 -->
# Use-Case APIs: Equipment Request Agent

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-006 |
| Document type | Use-Case APIs |
| Version | 0.1 |
| Status | In Review |
| Owner | API Design |
| Wave | Wave 1 |
| Canonical owner for | API-001 |
| Source evidence | Request API contract |
| Last updated | 2026-09-21 |

## API Inventory

API-001 implements the request operation for INT-001.

## API Contracts

### API-001 — Create Equipment Request

- **Functional IDs:** UC-001, FR-001, AC-001
- **Integration:** INT-001
- **Purpose:** Create the durable request.
- **Request mapping:** Item and justification come from confirmed inputs.
- **Response mapping:** Request ID and status become durable state.
- **Error mapping:** Validation returns correction; system failure follows recovery.
- **Idempotency and correlation:** A client request key prevents duplicates.
- **Authorization:** The authenticated employee may create a request.
- **Evidence:** Confirmed API contract.

## Cross-Use-Case Reuse and Sequencing

This operation is currently used only by UC-001.

## Contract Testing

AC-001 validates success and failure mappings.

## Open Questions

No blocking API question remains.
