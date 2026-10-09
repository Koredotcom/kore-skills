---
name: artemis-designer
description: Guide a Kore.ai agent from discovery material or an initial idea to a governed, modular enterprise design package. Use for guided discovery, drafting, updating, design review, gap analysis, wave readiness, or an implementation handoff. Do not estimate effort. Create or modify a Kore.ai project only after an explicit implementation request using available platform tools.
---

# Artemis Designer

Create or review an enterprise design package for a conversational, process, or hybrid Kore.ai agent. The package keeps business behavior, channel experience, and technical decisions in focused Markdown files governed by one design index.

## Choose the operating mode

- **Guide from scratch:** progressively discover the design from an idea.
- **Draft:** turn supplied discovery, requirements, diagrams, or SOPs into the modular package.
- **Review:** judge the substance and consistency of an existing design, including free-form or legacy documents.
- **Update:** incorporate new evidence or decisions while preserving identifiers, baselines, and traceability.
- **Prepare for implementation:** assess Wave 1 readiness and produce a bounded handoff.

Infer the mode when the request makes it clear. Ask only when the choice would materially change the work.

## Start with sources and destination

At the beginning, identify any supplied discovery intake, customer-approved scope artifact, requirements package, architecture material, or source-of-truth folder. Ask for relevant missing sources, especially the discovery intake or equivalent agreed scope. A discovery intake is preferred but is not required.

Request other relevant evidence—such as policies, process maps, brand/language guidance, sample interactions, and integration contracts—according to the agent's scope. Read supplied resources before asking questions they already answer. For thin or incomplete input, use [references/guided-intake.md](references/guided-intake.md) to prioritize missing facts across the whole design. Ask focused questions in manageable batches, not a fixed total number; do not prolong intake for details that can be marked provisional.

Distinguish customer-owned facts (which require evidence or an answer) from design choices (which can be recommended). Offer evidence-labelled recommendations together for confirmation or selective revision; a user's approval of recommendations does not establish customer approval of scope.

When no customer-agreed discovery artifact is available, continue and say once:

> We can proceed with the design. Phase and wave assignments will remain proposed and may need revision when the customer-agreed discovery scope becomes available.

Record the missing baseline as an open question and never imply that proposed scope is customer-approved.

Before creating or updating files, ask for the working folder unless the user already supplied an explicit destination. For a new package, create or use `<agent-slug>-design/` inside that destination. For an update, locate the existing `00-design-index.md` before editing. Do not default output into the installed plugin, source-artifact folder, or current shell directory.

## Preserve evidence and authority

Keep these states distinct:

- `Confirmed` — stated by the user or supported by supplied evidence.
- `Documented capability` — supported by current public product documentation or environment evidence.
- `Proposed` — a recommendation awaiting a decision.
- `Assumption` — a necessary working premise not yet confirmed.
- `TBD` — an unanswered design question.
- `Not verifiable` — requires unavailable product, environment, security, or architecture evidence.
- `Not applicable` — irrelevant to the design, with a reason.

Never present an inference as an existing capability or approved decision. Missing configuration, tool visibility, or secure values are evidence gaps, not proof that an integration or control does not exist.

## Read the applicable guidance

For every package creation or update, read [references/general-design-guidance.md](references/general-design-guidance.md) and [references/design-index-guide.md](references/design-index-guide.md) completely.

- For thin input or guided discovery, also read [references/guided-intake.md](references/guided-intake.md).
- For the shared agent charter and behavior, read [references/agent-definition-guide.md](references/agent-definition-guide.md).
- For each use case, read [references/use-case-guide.md](references/use-case-guide.md).
- For any material channel experience, first read [references/experience-design-guide.md](references/experience-design-guide.md). Then read [references/voice-experience-guide.md](references/voice-experience-guide.md) for voice or [references/digital-experience-guide.md](references/digital-experience-guide.md) for web, mobile, messaging, or email behavior.
- For technical work, read only the guides needed: [solution architecture](references/solution-architecture-guide.md), [connectivity and integrations](references/connectivity-integrations-guide.md), [use-case APIs](references/use-case-api-guide.md), [data and security](references/data-security-guide.md), and [operations, testing, and release](references/operations-testing-release-guide.md).
- For review or readiness, read [references/review-readiness-guide.md](references/review-readiness-guide.md).

Apply workflow rules in this file first, shared rules in the general guide second, and category-specific rules third. A category guide may specialize shared guidance but must not silently contradict it.

Load category guidance just in time. Do not read every technical and experience guide or fully pre-plan every document before creating the first supported files.

## Build the package progressively

Create only files supported by the current evidence, but establish the index first and keep it current:

```text
<agent-slug>-design/
├── 00-design-index.md
├── 01-agent-definition.md
├── use-cases/
│   └── UC-###-<slug>.md
├── experience/
│   └── <modality>.md
├── technical/
│   ├── architecture.md
│   ├── connectivity-integrations.md
│   ├── use-case-apis.md
│   ├── data-security.md
│   └── operations-testing-release.md
└── reviews/
    └── design-review.md
```

Omit category files that are not applicable and record that decision in the index. Keep Markdown as the canonical editable source. DOCX, PDF, or connected-document exports are derived outputs unless the user explicitly selects another authoritative source.

Work incrementally in this order:

1. Inventory the supplied evidence and distinguish confirmed scope from proposals.
2. Write the index, agent definition, and first Wave 1 use-case file as the minimum governed package. Register only files that exist, and include only identifiers already defined or created in the same increment.
3. Run the checker immediately and correct foundational metadata, link, identifier, prioritization, and wave warnings before expanding the package.
4. Create additional use-case, experience, and technical documents in small independent increments. Read each category guide immediately before that category and update the index with the same increment.
5. Run the checker after each material increment, then reconcile cross-document facts and perform the final semantic review.

Do not delay all writes while designing a warning-free final package in memory. A complete, evidence-labelled working draft is the first checkpoint; refinement follows validation. When a later-wave use case receives a `UC-###`, create at least its governed skeletal use-case file so the identifier has one canonical definition.

## Govern Wave 1

Use `Wave 1` as the canonical label and preserve `Phase 1` as a stated alias when supplied. The index owns all wave assignments.

Wave 1 must contain foundation work and at least one use case selected using explicit Value, Speed, and Readiness evidence. Preserve any customer-approved selection or documented override. The default planning target is delivery within 30 working days unless the supplied evidence establishes another target.

Do not estimate effort. Assess whether scope, dependencies, access, integrations, architecture, and readiness evidence support the target. A material feasibility concern prevents an implementation-ready verdict until scope, dependency, or target is resolved and recorded.

## Coordinate bulk work safely

When subagents are available and the source contains at least two substantial independent workstreams, the coordinator may delegate bounded use-case or category analysis.

- The coordinator reads the complete source inventory and exclusively owns the working folder, index, shared agent definition, identifier allocation, wave baseline, and change history.
- Give each subagent the relevant evidence, allocated identifiers, wave scope, general guide, and applicable category guide.
- Subagents return evidence-linked findings or edit only their assigned files; they never edit shared governance files.
- The coordinator reconciles contradictions, validates the complete package, and performs the final semantic review.

When subagents are unavailable, use the same sequence serially. Do not delegate merely because a source is long.

## Verify platform-specific claims

Use current public Kore.ai documentation or user-provided environment evidence when platform behavior affects the design. Record the source used. If authoritative evidence is unavailable, continue with product-neutral design and mark the choice `Not verifiable`.

Use only documentation and tools available to the user. Select a target environment explicitly before environment-specific discovery. Design and review requests do not authorize platform changes.

## Review and validate

Review facts across the complete package rather than treating a missing heading as a semantic defect. Legacy v1 functional and technical documents remain valid review inputs; migrate them only when the user asks to update or modularize them.

Run the advisory package checker after creating or updating a modular package:

```bash
python3 "${PLUGIN_ROOT}/skills/artemis-designer/scripts/check_design_structure.py" \
  --package "<agent-slug>-design"
```

When `PLUGIN_ROOT` is unset in a repository checkout, resolve the script relative to this `SKILL.md`. The checker verifies package structure, metadata, links, identifiers, manifest consistency, wave alignment, and traceability. It never replaces semantic review.

## Prepare the implementation handoff

When the readiness verdict permits setup, provide the approved Wave 1 scope, target product and environment, foundation, selected use case, dependencies, traceability, acceptance tests, blockers, and actions requiring authorization.

Platform mutation requires an explicit implementation request. After authorization:

Read the bundled [Artemis Developer skill](../artemis-developer/SKILL.md) and continue there with the existing working folder, design/index, approved scope, target facts, acceptance criteria, open decisions and authorization. Developer owns the concise architecture confirmation, incremental construction and evidence-based validation. Reuse explicit approval of the same concrete architecture; do not make users manually invoke the next skill or repeat setup.

If Developer is unavailable, provide the bounded implementation handoff and identify the missing capability. If platform tools are unavailable, Developer can prepare offline artifacts with explicit limits; neither skill should claim platform changes occurred. Design-only requests end with design/readiness outputs.
