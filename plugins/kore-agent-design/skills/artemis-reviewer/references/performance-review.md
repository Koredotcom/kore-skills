# Performance review

Read this when assigned the performance specialist role. Use the coordinator's context, matching design and source snapshot, existing session evidence, effective targets, and remaining test allocation. Follow [run-and-delegation.md](run-and-delegation.md) for shared limits and [platform-investigation.md](platform-investigation.md) for uncertain causes. Return evidence and recommendations; do not change the project during review.

## Establish what can be measured

Use explicit user or agreed design targets first. Otherwise use these review defaults, label them as defaults, and allow the user to override them:

| Channel | Default target | Measurement boundary |
|---|---|---|
| Chat | First meaningful visible response within 3 seconds | User submits the completed message to the first useful content rendered in the target channel. |
| Voice | First meaningful audible response within 2 seconds | User finishes speaking to the first useful content played to the caller, including end-of-speech detection. |

These are review heuristics, not a claimed platform SLA. Record the channel, definition, clock source, and effective target before assigning a timing verdict. Greetings, typing indicators, hold messages, and filler do not satisfy a task-response target unless that content itself fulfills the user's turn. Meaningful clarification can qualify; explain borderline cases.

Keep model time to first token, server event emission, debug reply completion, client rendering, first audio, and task completion as separate measures. Debug text cannot prove audible or rendered latency. If only server timings exist, report them with their actual boundary and leave channel target attainment unmeasured. Do not subtract timestamps from unrelated clocks without known synchronization. Distinguish cold sessions from later turns and meaningful initial response from completed answer or business action.

## Select targeted checks

Choose checks applicable to the design and use existing evidence before spending new calls. Announce selected scenario IDs and expected discriminating evidence to the coordinator. A conversation can satisfy multiple checks; shared sessions count once against the run allowance.

| ID | Exercise and inspect |
|---|---|
| PERF-01 | Compare an equivalent first request and later request. Separate initialization, routing, context growth, and channel delivery; keep session state differences visible. |
| PERF-02 | Compare configured streaming with delivered content. Inspect token/audio events and first useful output; identify buffering or filler that hides a slow answer. |
| PERF-03 | Follow one representative tool-heavy use case. Compare ABL dependencies and trace order; look for duplicate calls, repeated retrieval, redundant model passes, or avoidable serial steps. |
| PERF-04 | Continue, correct, or resume a task. Check context retention, repeated work, prompt growth, and whether a deterministic hybrid step could replace a measured reasoning pass while preserving behavior. |
| PERF-05 | Exercise an already permitted timeout, unavailable-service, or invalid-input case. Inspect bounded retries, total wait, recovery, and stalled turns. Never inject failure into an unapproved dependency. |
| PERF-06 | With real voice evidence, separate speech-end detection, recognition, routing, model, tool, synthesis, and audio delivery. Check interruption and cancellation costs where the design requires them. |
| PERF-07 | Investigate unexplained runtime gaps, duplicate processing, inconsistent timestamps, or ignored settings using one focused comparison. Preserve both passing and failing traces. |

Use wall-clock elapsed time for end-to-end latency. For overlapping spans, reconstruct dependencies and the critical path or a union of intervals; never add all durations as though they were sequential. Mark unexplained residual time and missing spans instead of assigning them to the model or platform. Describe optimization candidates as hypotheses until a comparison supports the causal claim.

## Report useful statistics and fixes

For each comparable group, give attempted count, valid measured count, missing measurements, timeouts, errors, and cancellations. Group by channel, source/runtime version, scenario, and cold/warm status when these differ materially. For valid samples report mean, median, maximum, and observed p95 with the method, for example nearest-rank. Include sample size beside every summary; a small-sample p95 is descriptive, not evidence of production tail latency. Do not drop timeouts silently, record them as zero, or combine a timeout cutoff with completed latency. Show measured target attainment as `within target / valid measurements` and separately show unmeasured or unsuccessful attempts.

For a finding provide the failing scenario/session/turn, elapsed boundary, relevant trace spans, matching ABL/prompt/configuration location when available, confidence, and a specific correction or next discriminating test. State the expected performance benefit and experience/correctness tradeoff. Prefer removing proven unnecessary work, using native ABL and HTTP/API capabilities, and suitable deterministic hybrid flow before proposing extra code or infrastructure.

Define verification using the same boundary and comparable conditions, plus a passing control that protects completion, confirmation, and recovery. A faster response that loses task context or executes an unconfirmed action is a regression. Use [findings-and-report.md](findings-and-report.md) for the common result format, retain raw evidence links, and stop at the assigned allowance rather than expanding the run to improve statistics.
