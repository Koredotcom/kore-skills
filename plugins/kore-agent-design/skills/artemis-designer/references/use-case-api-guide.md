# Use-case API guide

Read this reference when creating or updating `technical/use-case-apis.md`. Organize API contracts by operation and trace them to use cases; do not create a separate technical document per use case.

## Required structure

```markdown
<!-- kore-agent-design:use-case-apis:v2 -->
# Use-Case APIs: <Agent Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md.>

## API Inventory

| ID | Operation | Integration | Functional IDs | Side effect? | Contract status |
|---|---|---|---|---|---|

## API Contracts

### API-### — <Operation Name>

- **Functional IDs:** <UC/FR/AC references>
- **Integration:** <INT-###>
- **Purpose:** <business and technical purpose>
- **Interface and operation:** <method/event/operation without raw credentials>
- **Request mapping:** <field, source, requiredness, validation, transformation>
- **Response mapping:** <field, consumer, business meaning>
- **Error mapping:** <condition, user/process behavior, recovery>
- **Timeout and retry:** <policy>
- **Idempotency and correlation:** <keys and behavior>
- **Authorization:** <identity and permission requirement>
- **Evidence:** <contract source/version or Not verifiable>

## Cross-Use-Case Reuse and Sequencing

<Shared operations, ordering, transaction boundaries, concurrency, pagination, and caching.>

## Contract Testing

| API ID | Scenario | Related acceptance IDs | Fixture/environment | Expected evidence |
|---|---|---|---|---|

## Open Questions

| ID | Question | Affected API/use cases | Evidence needed | Owner | Blocking? |
|---|---|---|---|---|---|
```

## Category rules

- Define an `API-###` once and reference all consuming use cases.
- Trace every API to functional identifiers and every Wave 1 integration need to a contract or an explicit blocker.
- Distinguish confirmed contracts from proposed mappings and unavailable evidence.
- Never paste secrets, live tokens, customer records, or sensitive sample payloads.
- Define error and unknown-outcome behavior in terms the functional design can observe.
