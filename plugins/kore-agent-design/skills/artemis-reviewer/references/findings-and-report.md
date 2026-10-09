# Findings, coverage and metrics

One canonical results package belongs to each run. Preserve specialist notes and raw evidence separately. Do not require a private report skill, ticket system or external template. Markdown and JSON are the initial outputs; other requested formats may be derived without changing conclusions.

## Evidence and findings

Record scenario coverage as `scenario_id | requirement/check | expected | actual | status | snapshot | session/turn | evidence | finding IDs`. Status is Pass / Gap / Blocked / Not tested. A setup failure is Blocked; an executed behavioral failure is Gap. Omitted audio/rendering checks are Not tested. A passing refusal or workaround does not prove the entire business journey passed.

Every finding in `findings.json` has:

- `id`, `title`, `priority` (High / Medium / Low), `pillars` (experience, performance, architecture as applicable), affected requirement/check/scenario IDs, and concrete user impact.
- `snapshot_id`, expected/actual behavior, evidence links with session/turn and trace/source locations where available; missing links are explicit evidence gaps.
- `cause`, `confidence` (Confirmed / Suspected / Unknown), `boundary` (project / platform / provider / tooling / documentation / unknown), alternative explanations and contrary evidence.
- `recommendation`, expected benefit/tradeoffs, `verification` including passing regression controls, and `status` (Open / Repair proposed / Changed awaiting verification / Verified / Still failing / Deferred).

Use stable run-scoped finding IDs such as `RUN-001-F01`; retain original IDs through repairs. A static defect can have file/line evidence without a runtime session; label it static and keep runtime impact conditional. An unknown cause still permits an observed failure and a next discriminating test. Automated scans are leads; validate semantics before elevating them. Evidence must match the claimed snapshot. Never fabricate a source file, trace span, intended rule, successful action or platform bug.

Suggested JSON envelope: `schema_version`, `run_id`, `snapshot_id`, `mode`, `coverage`, `findings`, `limitations`, `specialist_artifacts`. This is a small interchange contract, not a proof verifier. Keep contextual text and evidence paths relative to the review workspace where possible; never include secrets in handoffs.

`report.md` leads with outcome and highest-impact findings, followed by scoped coverage, experience/performance summaries, prioritized repairs/investigations and limits. Link evidence and full findings rather than repeating transcripts. A clean static report cannot certify live behavior; a handful of live examples cannot certify production SLAs. Record sample size and unavailable channel/backend evidence.

## Metric observations

Use `results/metric-observations.json` as the metrics-helper input:

```json
{
  "schema_version": 1,
  "targets_seconds": {"chat": 3, "voice": 2},
  "observations": [
    {"snapshot_id": "sample-v1", "channel": "chat", "measurement": "visible_response", "session_id": "sample-session", "turn": 1, "status": "measured", "seconds": 3.4, "evidence": "evidence/sample-timing.json#turn-1"},
    {"snapshot_id": "sample-v1", "channel": "voice", "measurement": "audible_response", "session_id": "sample-call", "turn": 1, "status": "missing", "seconds": null, "evidence": "evidence/sample-transcript.md"}
  ]
}
```

Copy effective numeric targets from the frozen context, including user overrides; document their source there. Measurements: `visible_response` only for chat, `audible_response` only for voice, and `debug_response` for either channel. When debug evidence does not identify a chat/voice route, use `channel: "unknown"` with `debug_response`; do not infer a route from the design's supported channels. Debug measurements never count against actual-channel targets. Each snapshot/channel/measurement/session/turn key is unique; multiple kinds for one turn are allowed. Use `timeout` or `missing` with null seconds, not zero. Keep the underlying timestamps/clock definition and meaningful-output decision in referenced evidence.

The read-only helper rejects malformed rows, nonfinite/negative times, duplicates and incompatible channel/measurement pairs. It reports grouped mean, median, nearest-rank observed p95, maximum, measured target attainment and counts of measured/missing/timeout attempts. Distributions and target attainment use measured responses only; always report missing/timeouts alongside them to avoid survivorship bias. Empty groups have null statistics. Small samples and censored timeouts do not justify production percentiles or success claims.

The helper validates shape and computes numbers; it does not read referenced evidence, authenticate the collector, verify source identity, infer critical paths, or enforce execution budgets. The coordinator must check those separately. Keep task-completion time, model TTFT and STT/TTS/tool spans in additional clearly labelled evidence; do not relabel them as end-user response timing merely to fit this helper.
