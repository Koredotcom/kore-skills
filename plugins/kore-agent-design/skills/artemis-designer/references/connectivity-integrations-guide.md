# Connectivity and integrations guide

Read this reference when creating or updating `technical/connectivity-integrations.md`. This document owns system-level connectivity and integration behavior; endpoint-level contracts belong in the use-case API document.

## Required structure

```markdown
<!-- kore-agent-design:connectivity-integrations:v2 -->
# Connectivity and Integrations: <Agent Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md.>

## Integration Inventory

| ID | System | Purpose | Functional IDs | Environment availability | Owner | Status |
|---|---|---|---|---|---|---|

## Network and Connectivity

<Direction, protocols, domains or service references, private connectivity, firewall/proxy dependencies, certificates, DNS, and environment differences. Do not include secrets.>

## Authentication and Service Identity

<Authentication pattern, service/delegated identity, opaque credential-profile reference, token lifecycle, least privilege, and ownership.>

## Integration Behavior

### INT-### — <Integration Name>

- **Functional IDs:** <UC/FR/NFR references>
- **Business purpose:** <purpose>
- **Systems and direction:** <source and destination>
- **Trigger and consumers:** <events/use cases>
- **Data classes:** <classification without sensitive values>
- **Timeout and retry:** <policy>
- **Idempotency/correlation:** <strategy>
- **Error mapping:** <technical-to-business behavior>
- **Unknown-outcome verification:** <read-back or reconciliation>
- **Dependencies and ownership:** <access, environment, teams>

## Failure, Recovery, and Compensation

<Dependency outages, throttling, partial success, retry exhaustion, dead-letter/manual recovery, compensation, and status visibility.>

## Integration Decisions and Open Questions

| ID | Decision or question | Affected IDs | Evidence/owner | Status | Blocking? |
|---|---|---|---|---|---|
```

## Category rules

- Trace every `INT-###` to at least one `UC`, `FR`, or `NFR`.
- Distinguish connection availability from application-contract readiness.
- Record environment-specific dependencies without embedding credentials or private values.
- Give side-effecting operations idempotency or unknown-outcome handling proportional to their risk.
- Keep request/response fields in `technical/use-case-apis.md` and security controls in `technical/data-security.md`.
