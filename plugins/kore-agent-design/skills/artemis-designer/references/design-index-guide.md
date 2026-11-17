# Design index guide

Read this reference whenever creating, updating, or reviewing a modular package. The index is the governance record and authoritative source for document status and wave placement.

## Required index structure

Use this structure for `00-design-index.md`:

```markdown
<!-- kore-agent-design:index:v2 -->
# Agent Design Index: <Agent Name>

## Status Legend

| Term | Plain meaning |
|---|---|
| Confirmed | Supported by supplied evidence or an explicit answer; scope approval is recorded separately. |
| Documented capability | Product documentation or environment evidence supports this capability. |
| Proposed | A recommendation awaiting a decision. |
| Assumption | A working belief that still needs confirmation. |
| TBD | An answer or decision is still needed. |
| Not verifiable | The evidence needed to check this is unavailable. |
| Not applicable | This does not apply, with a stated reason. |

Document status: **Working Draft** means being written; **In Review** means awaiting review; **Approved** means accepted for the recorded scope/version; **Superseded** means replaced. Checklist status: **Pending** means not started; **In progress** means underway; **Blocked** means unable to proceed; **Complete** means finished with evidence; **Deferred** means explicitly moved outside this cycle with a follow-up; **Not applicable** means irrelevant with a reason. These describe different things; a confirmed fact does not approve a whole document.

## Reading Map

Start with the [Executive brief](00-business-brief.md). Business reviewers read the use-case and experience files assigned in the Sign-off Matrix. Technical reviewers read their assigned technical files. The coordinator reconciles the whole package; each reviewer reads only the files they sign.

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-000 |
| Document type | Design Index |
| Version | 0.1 |
| Status | Working Draft |
| Owner | <name or role> |
| Wave | All |
| Canonical owner for | Package governance, document register, wave scope, baselines, and change history |
| Source evidence | <sources> |
| Last updated | <YYYY-MM-DD> |

## Engagement and Design Context

<Business problem, intended outcome, sponsor or decision owner, agent type, target product, and delivery context.>

## Evidence Register

| Evidence ID | Source | Authority or owner | Date/version | Availability | Facts supported |
|---|---|---|---|---|---|

## Scope Baseline

**Baseline status:** Customer approved | Internally approved | Proposed | Not available

**Phase terminology:** <Wave 1, Phase 1, or mapping>

**Target:** <30 working days or supplied target>

<Confirmed scope, exclusions, customer agreement evidence, and any provisional-scope notice.>

## Document Register

| Document ID | Document | Type | Version | Status | Wave | Canonical ownership |
|---|---|---|---|---|---|---|
| <allocated DOC ID> | [Executive brief](00-business-brief.md) | Executive Brief | 0.1 | Working Draft | All | Derived summary; owner: <business owner> |
| DOC-001 | [Agent Definition](01-agent-definition.md) | Agent Definition | 0.1 | Working Draft | All | Shared agent behavior |

## Kickoff decisions and customer actions

| Decision or access item | Customer owner | Needed-by date | What it blocks | Status | Canonical evidence / next action |
|---|---|---|---|---|---|

<Include every outstanding customer decision or access prerequisite, including measurement facts, scope decisions and environment/API access. Link to its canonical open question or dependency. Use an actual date when known; otherwise TBD with an action to agree it. Never infer a customer owner, date or completion. If none remain, state None with evidence.>

## Sign-off Matrix

| File | Version | Review area | Reviewer / customer role | Status | Decision evidence / date | Next action |
|---|---|---|---|---|---|---|

<One row per file and reviewer assignment. Business signs each use-case and experience file; technical signs each technical file. Assign the brief and shared agent definition to the business owner, and the index/review to the design coordinator. Use Pending, In review, Approved, Changes requested, or Not applicable with rationale. Record actual decision evidence, date and version; do not infer sign-off from scope approval or file creation.>

## Foundation Register

| ID | Foundation item | Wave | Status | Dependencies | Evidence or owner |
|---|---|---|---|---|---|
| FND-001 | <platform, environment, channel, identity, integration, governance, or operational foundation> | Wave 1 | Proposed | <dependencies> | <evidence> |

## Design Completion Checklist

**Finalization scope:** <deliverables and wave covered by this design cycle; exclusions and later-wave treatment>

| Task | Stage | Scope | Status | Evidence or rationale | Next action / owner | Updated |
|---|---|---|---|---|---|---|
| Confirm source inventory and scope | Discovery | <source and scope references> | Pending | <known evidence or gap> | <next action and owner> | <YYYY-MM-DD> |
| Draft executive brief | Draft | 00-business-brief.md | Pending | <canonical facts summarized> | <next action and owner> | <YYYY-MM-DD> |
| Resolve kickoff decisions and customer actions | Discovery | <kickoff table items and outcomes> | Pending | <known decisions, owners and dates> | <next action and owner> | <YYYY-MM-DD> |
| Draft shared behavior | Draft | <agent-definition path; link once created> | Pending | <evidence when drafted> | <next action and owner> | <YYYY-MM-DD> |
| Check package structure | Validation | <current package revision> | Pending | <dated check result and warning dispositions> | <next action and owner> | <YYYY-MM-DD> |
| Review design substance and traceability | Validation | <scoped files and versions> | Pending | <semantic findings and resolutions> | <next action and owner> | <YYYY-MM-DD> |
| Confirm design decisions and baseline | Approval | <scoped files and versions> | Pending | <actual confirmation reference, actor, date and scope> | <next action and owner> | <YYYY-MM-DD> |
| Finalize scoped design package | Finalization | <finalization scope> | Pending | <gate evidence and final verdict> | <next action and owner> | <YYYY-MM-DD> |

<Expand Draft tasks for each use case (including both Wave 1 samples), applicable experience modality and technical document. Validation covers the brief, metrics, use-case goal tests, conversations, kickoff items and sign-off coverage. Track validation and approval coverage separately; approval tasks link the Sign-off Matrix, and grouped tasks enumerate their covered files and versions.>

## Use-Case Prioritization

| Use case | Value (1–5) | Speed (1–5) | Readiness (1–5) | Score | Selection rationale | Evidence status |
|---|---:|---:|---:|---:|---|---|
| [UC-001](use-cases/UC-001-<slug>.md) | <value> | <speed> | <readiness> | <product> | <reason or override> | <Confirmed, Proposed, or Not verifiable> |

## Wave Plan

| Use case | Wave | Scope status | Foundation dependency | Target outcome | Customer agreement |
|---|---|---|---|---|---|
| [UC-001](use-cases/UC-001-<slug>.md) | Wave 1 | Confirmed | FND-001 | <outcome> | <evidence or Not available> |

## Traceability Summary

| Business outcome or requirement | Canonical design | Technical treatment | Acceptance evidence | Coverage status |
|---|---|---|---|---|

## Experience Decision Summary

| Experience ID | Canonical decision | Confirmation status | Affected use cases or waves | Next action |
|---|---|---|---|---|

<Link only material EXP decisions. The experience file owns their full rationale, evidence, and approval record; update this summary in the same increment as a material decision change.>

## Decisions and Changes

### Confirmed decisions

| Decision | Rationale | Evidence or approver | Date | Affected IDs |
|---|---|---|---|---|

### Change history

| ID | Change | Baseline affected | Affected IDs/documents | Owner | Approval status | Effective version |
|---|---|---|---|---|---|---|

## Risks, Dependencies, and Open Questions

### Risks and dependencies

| Item | Impact | Owner | Due date or trigger | Status |
|---|---|---|---|---|

### Open questions

| ID | Question | Why it matters | Owner or evidence needed | Blocking? | Affected IDs |
|---|---|---|---|---|---|

## Readiness Snapshot

<Current verdict, checklist progress, critical blockers, Wave 1 feasibility, and next unfinished action. Distinguish a working draft, validated design, and approved/finalized scope.>
```

## Wave governance rules

- Use `Wave 1` as the canonical label and record any supplied `Phase 1` terminology as an alias.
- Preserve a customer-approved baseline. Mark proposed changes separately and never rewrite the approved record silently.
- When customer-approved discovery evidence is unavailable, set the baseline to `Proposed`, assign an `OQ-###`, and keep wave assignments provisional.
- Wave 1 includes foundation plus at least one use case. Record Value, Speed, and Readiness scores only when supplied or explicitly confirmed; never invent them.
- Verify score arithmetic deterministically when scores are present. A lower-scoring selection needs a documented reason.
- Use 30 working days as the default Wave 1 planning target unless the evidence establishes another target. Assess feasibility from scope and readiness evidence without inventing an effort estimate.
- Keep later-wave items visible with exclusions and prerequisites so deferred scope cannot disappear.

## Index maintenance rules

- Update the document register whenever a file is added, renamed, superseded, or changes status, version, or wave.
- The index links to every canonical package document. A document absent from the register is outside the governed package.
- Update the traceability summary after material functional or technical changes.
- Keep the experience decision summary synchronized with applicable voice and digital files; do not treat a user's confirmation of design recommendations as customer approval of the scope baseline.
- Record only a concise readiness snapshot; keep detailed findings in `reviews/design-review.md`.
- Present the executive brief first in the register and reading order. Its allocated document ID and governance fields belong here only; all other files retain their own metadata. Refresh the brief with changes to its canonical sources.
- Maintain kickoff actions and file-scoped sign-offs with every material decision. Each reviewer reads only the files they sign; the coordinator owns cross-file consistency and routes changes to affected reviewers. A reviewer can sign multiple explicitly assigned files. Do not make business readers approve technical contracts or require technical reviewers to sign business behavior by default.
- Keep sign-off separate from requested scope: a draft-only assignment may mark approval Not applicable with that boundary, while approved/finalized deliverables require the actual assigned decisions. Reopen affected sign-offs and approval tasks on material changes; retain earlier evidence in change history.

## Active checklist lifecycle

The Design Completion Checklist is the persistent work record for the current design cycle. Create it with the index and maintain it through discovery, drafting, validation, approval and finalization. Its task statuses are separate from document metadata statuses and review criterion statuses.

- Use stages `Discovery`, `Draft`, `Validation`, `Approval`, and `Finalization`. Include all stages from the start, even when work has not reached them. For a partial design assignment, state its bounded finalization scope; do not imply the entire implementation design is complete.
- Use statuses `Pending`, `In progress`, `Blocked`, `Complete`, `Deferred`, or `Not applicable`. Every row needs a specific task, scope, next action/owner, and last-updated date. For a closed row, the next-action cell may say `None — <accountable owner>`.
- Create one drafting task for the executive brief, agent definition, each identified use case (including later-wave skeletons), each applicable experience modality, and each required technical document. Track the two sample conversations within each Wave 1 use-case task, and track customer kickoff actions through resolution. Add tasks as scope becomes known. Planned paths remain plain text until files exist; then use relative links. The document register still lists only existing documents.
- Track structural checks and semantic review separately. Record the checked revision or file versions, date, result, and disposition of warnings/findings. A passing checker alone does not complete semantic review or prove approval. Keep detailed findings in the review file and link them.
- Keep approval tasks separate from drafting and validation, with the actual confirmation source, actor, date and covered scope/version. Reuse existing valid confirmations; do not introduce an extra approval ceremony. If approval is not part of the requested deliverable, mark it `Not applicable` with that boundary and label the output accordingly. Never label such a draft customer-approved.
- `Complete` requires evidence of the task's outcome. `Deferred` needs a reason, agreed scope/wave disposition and a follow-up action/owner; `Not applicable` needs a reason. Missing information or unavailable checks remain `Pending` or `Blocked`, not `Complete`. Do not defer an unresolved blocker merely to finalize.
- Update affected rows with each material file increment, validation run, finding or decision, and before a pause or handoff. On resume, reconcile saved status with current files and evidence before selecting the next unfinished task. Avoid rebuilding the plan from chat memory.
- Reopen tasks whose evidence was invalidated by a change, including dependent validation, approval and finalization tasks. Preserve earlier results and approvals in change history, then record the new scope/version; do not silently carry approval to changed behavior.
- For an older modular package, add the checklist during an authorized update and derive statuses only from available evidence. Review-only work may report its absence without rewriting the input. Legacy v1 review remains supported.

Keep rows concise and link canonical design content instead of embedding functional SOPs, journey walkthroughs or technical specifications in the index. Before finalization, compare the checklist with the document register, wave scope and applicable category requirements so omitted work cannot disappear behind completed rows. Apply the review guide's finalization gate and update the readiness snapshot in the same increment.
