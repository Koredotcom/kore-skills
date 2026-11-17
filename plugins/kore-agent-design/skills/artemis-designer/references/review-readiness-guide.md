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
- identifiers are stable, unique, defined, referenced, and not silently reused;
- the active checklist covers the scoped deliverables, separates drafting from validation and approval, and agrees with current files, findings and confirmation evidence; and
- derived exports are not competing editable sources.

Also check the one-page executive brief is first, readable without IDs and consistent with canonical scope, KPIs, exclusions, risks and readiness; the index begins with a plain status legend; and kickoff decisions/access actions name the customer owner, needed-by date and blocked work. Missing facts must be explicit owned gaps, not invented dates or approvals. Verify the Sign-off Matrix covers current files/versions: business reviews use cases and experience, technical reviews technical files, and each reviewer reads only their assigned sign-off files. The coordinator reconciles cross-file facts.

## Functional and experience review

Check that:

- the agent charter, users, authority, common behavior, scope, and outcomes are usable;
- every in-scope use case has reconstructible paths, branches, failures, terminal states, integrations, and acceptance criteria;
- long-running work defines identity, persistence, waits, human-task authorization, deadlines, resumption, cancellation, recovery, and audit;
- handoff and process approval are distinct;
- applicable modalities have category-specific behavior and failure handling; and
- critical journeys and EXP decisions are understandable to a customer, linked to functional sources and acceptance evidence, and clearly marked proposed or confirmed; and
- voice covers listener-appropriate voice/accent and rate rationale, pronunciation, turn-taking, silence, interruption, recognition, confirmation, latency, transfer, sensitive values, accessibility, and rendered-audio testing.

Apply these business-readability checks as semantic findings, not merely heading checks:

- Each use case passes the standalone-contact and completed-result tests in the use-case guide (or the sole-purpose trigger and completed-outcome equivalent for process agents). Flag authentication, identity checks and capture steps promoted to use cases without an independent user goal. Flag generic labels such as “Handle incoming users”, “Manage customer queries” or “Process requests”, and labels that combine goals; propose a specific verb/object name or split.
- Every business outcome has a comparable baseline, target and measurement source. An explicit TBD is a tracked gap, not a measured success; assess whether it blocks the next decision.
- Every Wave 1 use case has a happy-path and failure-path Speaker/Message sample through a clear result. For process-only agents, verify equivalent event/result exchanges without an invented conversational interface. Samples must agree with the SOP, business rules, modality decisions and acceptance criteria; examples are not runtime evidence. Diagrams are optional for many branches.
- Trigger, Actors and Preconditions are explicit, and functional SOPs describe business actions rather than API calls, endpoints or payloads. Keep contract references in Integration and API Needs.

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

## Design finalization gate

Finalization applies to the explicitly recorded design scope; it does not itself authorize a build or prove implementation readiness. A functional-design-only assignment may finish while technical design remains a later task. State that boundary in the index and final response.

Before marking the checklist's Finalization task `Complete`:

1. Reconcile the checklist against the source scope, document register, executive brief, business outcome measures, kickoff actions, every in-scope use case (including Wave 1 samples), applicable experience modalities and required technical categories. Preserve the separate canonical files and resolve missing coverage.
2. Complete structural validation and semantic review for the current versions. Resolve material findings; record justified dispositions for nonblocking warnings. The advisory checker's exit code is not a finalization verdict.
3. Resolve required confirmation and approval tasks against the file-scoped Sign-off Matrix using actual evidence for the current versions. Explicit exclusions or agreed deferrals must have rationale, scope/wave treatment and a follow-up owner where needed. Required unresolved work or blockers prevent finalization; never substitute deferral for required approval.
4. Ensure all other tasks are `Complete`, `Deferred`, or `Not applicable` with the required evidence/rationale. Update document statuses, index metadata, checklist evidence, review findings, kickoff actions, sign-offs and readiness snapshot consistently; refresh the brief last against those canonical facts. The finalization row must cite the reconciled scope/version and verdict.

If the gate is not met, deliver the useful draft or review with its unfinished checklist and next actions. `READY WITH TRACKED GAPS` is a bounded handoff verdict, not proof that the entire design is finalized. A missing checklist in an older review input is a tracking gap, not automatic evidence that its design substance is invalid; do not rewrite that input without an update request.

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
