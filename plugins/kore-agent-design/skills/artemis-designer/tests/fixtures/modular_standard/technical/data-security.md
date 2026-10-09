<!-- kore-agent-design:data-security:v2 -->
# Data and Security: Equipment Request Agent

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-007 |
| Document type | Data and Security |
| Version | 0.1 |
| Status | In Review |
| Owner | Security Architecture |
| Wave | Wave 1 |
| Canonical owner for | TD-002 and authorization controls |
| Source evidence | Security review |
| Last updated | 2026-09-21 |

## Data Inventory and Classification

Employee identity, item, justification, and decision are retained in the request system.

## User, Service, and Human-Task Identity

Employee and manager identity originate from the approved identity provider.

## Authorization Model

BR-001 is enforced before the manager decision is accepted for UC-001.

## Data Lifecycle and State

Conversation state is separate from durable request state under NFR-001.

## Privacy, Compliance, and Consent

Logs omit unnecessary employee content.

## Threats and Security Controls

Least privilege and audit evidence protect consequential actions.

## Security Decisions and Open Questions

### TD-002 — Enforce least privilege at the action boundary

UC-001 and BR-001 require the decision service to verify manager authority.
