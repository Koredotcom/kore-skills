# Useful speed and experience

Read during architecture selection and latency-sensitive changes. Optimize the shortest practical time to a correct useful response and completed task, with agreed comprehension, control and recovery intact.

## Choose and measure together

Trace the actual critical path: model work, routing, tool calls, serialization, rendering and speech stages. Separate overlapping intervals rather than adding all span durations. Reduce unnecessary model calls/handoffs and repeated collection, use relevant context, and choose model roles against task quality. Use supported streaming or parallel independent reads only where dependencies and user experience permit. Hybrid execution can improve predictability; a speed advantage remains a hypothesis until observed.

Record scenario, source version, channel, session/turn, start/end event definition and evidence. Measure:

- first meaningful visible response in chat or audible response after user speech;
- full response and end-to-end business completion time;
- total user turns, repeated questions, retries, failures and abandonment/recovery observations;
- correctness, comprehension, confirmation and recovery acceptance alongside timing.

Keep model TTFT, debug completion time, rendered chat and actual audio timing separate. A typing indicator or filler does not satisfy meaningful-response acceptance. Include failed/time-out cases and disclose small samples; report available distributions without pretending a few tests certify production SLAs.

Use design/customer targets or label proposed review targets explicitly. Unknown channel delivery timing stays unmeasured. Do not claim the prompt's requested timeout or latency budget is an enforced runtime setting.

## Improve without irritating

Reuse already supplied facts. Group related questions only when easy to answer. Avoid serial confirmations of unchanged low-risk details, generic acknowledgements on every turn and excessive progress messages. Give an occasional honest progress cue for a real delay and a recovery path when work cannot finish. Do not truncate essential results, suppress consequential confirmation, interrupt pauses or accelerate speech until comprehension suffers.

For a working flow, compare a representative before/after journey with matched data and source versions. Retain the optimization only if useful timing or effort improves without regressing business success, clarity, privacy or recovery. If a speed/quality tradeoff needs a product decision, show it in the brief rather than silently accepting the loss.

Preserve session/correlation IDs and minimal diagnostic evidence while respecting data restrictions. Avoid concurrent tests that distort latency measurements or share mutable records.
