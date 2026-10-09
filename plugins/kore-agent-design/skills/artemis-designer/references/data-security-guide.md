# Data and security guide

Read this reference when creating or updating `technical/data-security.md`.

## Required structure

```markdown
<!-- kore-agent-design:data-security:v2 -->
# Data and Security: <Agent Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md.>

## Data Inventory and Classification

| Data element or class | Source of truth | Classification | Used by | Storage/state | Retention/deletion | Owner |
|---|---|---|---|---|---|---|

## User, Service, and Human-Task Identity

<Identity sources, trust, session binding, service identities, approver identity, delegation, and reauthentication.>

## Authorization Model

| Action or resource | Actor | Authorization rule | Enforcement point | Failure behavior | Functional IDs |
|---|---|---|---|---|---|

## Data Lifecycle and State

<Collection, validation, minimization, conversation context, durable state, encryption expectations, access, logging restrictions, retention, deletion, concurrency, and source of truth.>

## Privacy, Compliance, and Consent

<Applicable requirements supplied by the user, consent/disclosure, data residency, regulated decisions, human oversight, and evidence needed.>

## Threats and Security Controls

| Threat or misuse | Impact | Control | Detection/evidence | Owner | Status |
|---|---|---|---|---|---|

## Security Decisions and Open Questions

| ID | Decision or question | Affected IDs | Evidence needed | Owner | Blocking? |
|---|---|---|---|---|---|
```

## Category rules

- Define sources of truth and distinguish transient conversation context from durable business state.
- Trace consequential actions to explicit authorization rules and enforcement points.
- Use data minimization and opaque secret/profile references. Never include raw credentials or sensitive customer examples.
- Treat missing exported secure values as unavailable evidence, not proof that authentication is absent.
- Record only compliance requirements supported by supplied or authoritative evidence.
- Make logging restrictions and audit needs specific enough for operations and testing.
