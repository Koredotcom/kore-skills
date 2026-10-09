<!-- kore-agent-design:connectivity-integrations:v2 -->
# Connectivity and Integrations: Equipment Request Agent

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-005 |
| Document type | Connectivity and Integrations |
| Version | 0.1 |
| Status | In Review |
| Owner | Integration Architecture |
| Wave | Wave 1 |
| Canonical owner for | INT-001 |
| Source evidence | Request-system integration notes |
| Last updated | 2026-09-21 |

## Integration Inventory

INT-001 connects the agent workflow to the request system for UC-001.

## Network and Connectivity

Outbound HTTPS connectivity is environment-specific under FND-001.

## Authentication and Service Identity

An opaque service credential profile is used.

## Integration Behavior

### INT-001 — Request System

- **Functional IDs:** UC-001, FR-001, AC-001
- **Business purpose:** Create and update an equipment request.
- **Timeout and retry:** Bounded retry applies to safe failures.
- **Idempotency/correlation:** The request ID prevents duplicate creation.
- **Unknown-outcome verification:** Read the request before retrying.

## Failure, Recovery, and Compensation

Unknown outcomes are verified and support receives unrecoverable failures.

## Integration Decisions and Open Questions

No blocking integration question remains.
