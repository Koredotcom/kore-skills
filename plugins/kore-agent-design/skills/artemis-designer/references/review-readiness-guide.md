# Design review and readiness guide

Read this reference for package review, update impact review, or implementation readiness. Review the complete artifact set and judge facts wherever they appear.

## Criterion statuses

Use `Complete`, `Partial`, `Missing`, `Conflicting`, `Not verifiable`, or `Not applicable`. Do not calculate a numerical quality score.

## Package governance review

Check that:

- the index lists every canonical document and agrees with document metadata;
- evidence authority, baseline state, owners, versions, statuses, and wave assignments are explicit;
- each fact has one canonical owner and links resolve to that source;
- approved scope changes have `CHG-###` records and affected documents were reconciled;
- identifiers are stable, unique, defined, referenced, and not silently reused; and
- derived exports are not competing editable sources.

## Functional and experience review

Check that:

- the agent charter, users, authority, common behavior, scope, and outcomes are usable;
- every in-scope use case has reconstructible paths, branches, failures, terminal states, integrations, and acceptance criteria;
- long-running work defines identity, persistence, waits, human-task authorization, deadlines, resumption, cancellation, recovery, and audit;
- handoff and process approval are distinct;
- applicable modalities have category-specific behavior and failure handling; and
- critical journeys and EXP decisions are understandable to a customer, linked to functional sources and acceptance evidence, and clearly marked proposed or confirmed; and
- voice covers listener-appropriate voice/accent and rate rationale, pronunciation, turn-taking, silence, interruption, recognition, confirmation, latency, transfer, sensitive values, accessibility, and rendered-audio testing.

## Technical review

Check that:

- architecture is bounded and components trace to functional or non-functional needs;
- environments, promotion, state ownership, workflow responsibilities, model/prompt/tool/knowledge design, and guardrails are defined;
- integrations and APIs specify contracts, mapping, authorization, timeouts, retries, errors, idempotency, and unknown-outcome handling;
- data, identity, security, privacy, retention, observability, operational ownership, testing, release, and rollback are actionable; and
- product-specific claims have current evidence or are marked `Not verifiable`.

Treat material missing source facts differently from confirmable design recommendations. Verify that supplied resources were used, essential gaps were asked with purpose, and provisional scope was not silently promoted to approved. Do not fail a design merely because a recommendation awaits user confirmation; identify its impact on the next readiness stage.

## Wave 1 readiness gate

An implementation-ready verdict requires:

- a customer-approved scope baseline or explicit acknowledgement that approval remains blocking;
- foundation plus at least one fully designed Wave 1 use case;
- defensible Value, Speed, and Readiness evidence and any selection override;
- a credible path to the 30-working-day default target or another confirmed target, based on known scope, access, dependencies, architecture, integrations, and data;
- acceptance and release evidence covering the Wave 1 outcome; and
- blockers and external actions with owners and dates.

Do not estimate effort. When evidence cannot support the target, identify the exact scope, dependency, or decision that must change.

## Readiness verdicts

- `NOT READY` — a missing fact or conflict makes the next stage materially wrong or unsafe.
- `READY FOR TECHNICAL DESIGN` — functional and experience scope are designable, but material technical decisions remain.
- `READY WITH TRACKED GAPS` — a bounded first setup slice can start safely while named nonblocking gaps remain.
- `READY FOR PROJECT SETUP` — Wave 1 foundation and the first implementation slice are supported with no critical blocker.

## Finding format

Write each finding as:

> missing, weak, or conflicting fact → effect on design or implementation → exact question or action → affected identifiers and documents

## Fixed review output

```markdown
<!-- kore-agent-design:review:v2 -->
# Agent Design Review: <Agent Name>

## Document Metadata

<Use the metadata block from general-design-guidance.md.>

## Headline

<Overall readiness and principal reason.>

## Readiness Verdict

NOT READY | READY FOR TECHNICAL DESIGN | READY WITH TRACKED GAPS | READY FOR PROJECT SETUP

## Critical Blockers

<Blocking findings, or None.>

## Package Governance

<Metadata, ownership, baseline, wave, change-control, link, and identifier findings.>

## Functional and Experience Coverage

<Material gaps or conflicts.>

## Technical Coverage

<Material gaps or conflicts.>

## Traceability and Drift

<Unmapped requirements, unjustified components, duplicate facts, stale references, or no material gap.>

## Wave 1 Feasibility

<Foundation, selected use case, target, dependencies, evidence, and blockers.>

## Findings

### <Finding title> — <Status>

**Evidence:** <quote/reference or not stated>

**Impact:** <effect>

**Ask or action:** <exact resolution>

**Affected IDs/documents:** <references>

## Questions to Resolve

<Short ordered questions.>

## Recommended Next Step

<Smallest useful action; include a bounded handoff only when allowed by the verdict.>
```

List every critical blocker and material contradiction. Avoid cataloging every correct fact when the package is ready.
