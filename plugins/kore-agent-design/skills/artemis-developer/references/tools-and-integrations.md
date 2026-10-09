# Native logic and integration tools

Read before choosing a tool type, writing request/response mappings or changing a business-action path.

## Decision order

1. Put supported capture/state/control, branching, confirmation and validation in native ABL. Inspect current expression/function and execution documentation; lack of familiarity is not a capability gap.
2. Use HTTP/API tools or an existing appropriate supported integration for external operations. Use documented native request/response mapping and transformations where sufficient. Keep backend authorization and business truth at their authoritative boundary.
3. Consider a Code Tool only for a concrete unmet requirement after checking native alternatives. Record the requirement, alternatives/evidence, narrow code boundary, data handling, verification and latency/maintenance implications. Include the exception in the architecture brief and obtain confirmation before implementing it.

Do not invent ABL syntax, use a script merely to wrap a standard API call, or introduce a new service just to move avoidable code elsewhere. A genuine native gap is a reasoned exception, not a reason to force incorrect native behavior.

## Contract before implementation

For each tool record method/path or opaque service reference, typed inputs, required/default/optional values, identity/auth-profile reference, time/locale units, success and business-error envelopes, side effects, retry/idempotency semantics and consumer mappings. Use synthetic payloads; keep credentials out of files.

Preserve opaque references byte-for-byte unless the contract permits normalization. Validate time/date transformations at boundaries. Verify protected-value restoration before raw-format checks; missing/redacted secret values in an export do not establish missing authentication.

Separate transport failure, malformed response, business refusal, empty successful result, partial success and confirmed completion. Order result-dependent checks after the current tool call completes. A 200 response with a business-error status is not success; a successful request without a durable result may need read-back.

## Side effects and uncertain outcomes

Bind consequential actions to the exact confirmed values and authoritative permission check. Use the backend's supported idempotency/correlation mechanism. Do not invent a key format or claim deduplication without evidence. A timeout after submission requires checking the known action/operation status before deciding whether to retry; never replay an unresolved mutation blindly.

Retry only eligible failures within the run's allowance, with bounded backoff. Preserve cancellation and user-visible recovery during delay. Independent reads can run concurrently when supported; writes with shared inventory/identity/state usually need ordering. A faster race is not an improvement.

**Example:** a catalog lookup returns an item reference and availability. Map the current response to typed state, handle unavailable items, confirm the selected item/period, then submit through the booking API. A separate JavaScript validation tool is unnecessary when documented ABL and native mappings meet that contract.

Verify success, business refusal, malformed/empty response, timeout with unknown outcome and duplicate submission. Execute against approved fixtures or permitted records; documentation and compiler success alone do not verify an integration.
