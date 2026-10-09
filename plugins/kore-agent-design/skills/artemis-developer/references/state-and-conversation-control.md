# State and conversation control

Read before capture, correction, confirmation, cancellation, delegation or resume logic.

| Situation | Implement | Avoid | Verification |
|---|---|---|---|
| First utterance contains several fields | Reuse supported typed values with provenance; clarify only missing/ambiguous facts | Dropping input during routing or asking for every field again | Send a complete request in one turn, then a partial one |
| User corrects a captured value | Update dependent state, invalidate stale calculations and confirmation | Acting on an old reviewed value | Change a consequential field just before submission |
| Cancel/back/help during collection | Define reachable handling in each relevant state and preserve or clear data intentionally | Waiting until the final confirmation to recognize cancel | Cancel during each distinct collection/lookup stage |
| Tool result is pending/failed | Consume the current completed result and map failure to recovery | Checking an uninitialized/previous response or continuing a success branch | Timeout, empty result and business refusal |
| Handoff completes | Return a typed outcome and clear only state owned by the completed task | Closing the whole session unintentionally | Complete one task, then ask for a different task |
| Duplicate input or resume | Correlate with prior state/action outcome and apply the documented policy | Repeating a side effect or resetting test/run history | Replay input after a delayed response |

Keep raw user wording distinct from normalized contract values and opaque references. Normalize dates/times using a known locale/timezone; preserve separators in identifiers unless the contract explicitly permits change. Do not treat protected identity tokens as raw email/phone values. Inspect the platform's restoration and transformation boundaries before applying format checks.

Tie consent to the exact consequential fields shown to the user. Changing those fields invalidates prior confirmation. Avoid reconfirming unchanged low-risk information merely to fill a step. Tool success must establish the actual business outcome; transport success alone may carry a refusal.

Distinguish transient conversation state, durable business state and proposed actions. Resume semantics, expiry and idempotency depend on the actual backend/runtime. Do not promise persistence from an in-memory variable. Preserve unresolved outcomes until reconciled, and do not fabricate a reference or final status.

Use native state/control constructs supported by the target. If a construct cannot handle the required interruption or return contract, revise the design or propose a supported alternative before broadening the implementation.
