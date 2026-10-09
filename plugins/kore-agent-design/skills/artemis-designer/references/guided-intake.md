# Guided intake

Use this reference when the user starts from an idea, thin notes, or incomplete evidence. The goal is a productive design conversation, not completion of a questionnaire.

Read provided files before questioning. Ask a manageable batch of related, material questions—normally three to five at a time, not a lifetime cap. Prefer questions the current user can answer; name the owner or evidence source needed for others. After each meaningful round, summarize what is confirmed, proposed, assumed, open, and ready to draft. Stop asking when a coherent working design can be produced with explicit gaps; return only when a material answer is needed.

The rounds below are a coverage map, not six mandatory interview sessions. Skip topics covered by supplied evidence, combine related questions, and move to a working draft when the core design is coherent.

Do not repeat answered questions because the answer appeared in an unexpected source. Do not block on noncritical unknowns. Assign an `OQ-###` when an unresolved point affects scope, wave placement, behavior, architecture, security, or readiness.

## Opening: sources and working folder

Ask for:

- a discovery intake or equivalent customer-approved scope artifact;
- relevant requirements, SOPs or process maps, policies and guardrails, architecture and API material, brand/language guidance, sample interactions, and a source-of-truth folder;
- the target working folder for generated files; and
- whether an existing modular package should be updated.

Explain why a requested resource matters; do not impose a checklist when a category is irrelevant. Let the user supply a source instead of answering facts already documented in it. If customer-agreed discovery evidence is unavailable, continue with the provisional-scope notice in `SKILL.md`. Do not ask for the working folder again when an explicit destination was already provided.

## Facts, recommendations, and blockers

- Ask for customer-owned facts that cannot responsibly be inferred: intended users and outcomes, scope and exclusions, channels, consequential policies, constraints, and ownership. Prioritize unknowns that change Wave 1 feasibility, safety, or core behavior.
- Recommend design choices where reasonable, including channel experience, voice character, pacing, confirmation, and recovery. Show rationale and evidence status, then let the user confirm all recommendations or alter selected ones. Update linked documents after confirmation without repeating the question.
- A missing fact that materially blocks a section remains a named open question with owner and needed source. A nonblocking detail may remain an explicit assumption or `TBD`; it does not prevent a working draft. Do not call a provisional section final or treat user approval of a design proposal as customer-approved discovery scope.

For a batch of choices, show the decision, recommendation, source or rationale, what confirmation is needed, and the canonical document that will own the result. Record who confirmed a choice and when if that information is available.

## Round 1: agent charter

Discover enough to state:

- the business problem and why an agent is appropriate;
- primary users, decision owners, and stakeholders;
- initiating events or user requests;
- desired outcomes and measurable success;
- agent boundaries and explicit exclusions; and
- likely operating model: conversational, process, or hybrid.

Draft the index context and agent definition as soon as this is stable enough. Explain the signals behind the proposed operating model.

## Round 2: scope, waves, and priority

Inventory distinct business outcomes and separate them from welcome behavior, fallback, reminders, lifecycle hooks, and generic escalation. For each candidate use case, capture:

- trigger, actors, outcome, volume, and business value;
- main steps, variations, failures, systems, and data;
- access, API, content, environment, and owner readiness;
- foundation dependencies and channel/language needs;
- Value, Speed, and Readiness scores when supplied or explicitly confirmed; and
- proposed or approved wave placement.

Preserve a customer-approved Wave 1 selection. When scope is only proposed, label it accordingly. Wave 1 contains foundation plus at least one use case and defaults to a 30-working-day planning target unless another target is confirmed.

## Round 3: use-case SOPs

Work through one use case or a small related group at a time. Ask for business-level steps, inputs and validation, rules, branches, terminal outcomes, correction, handoff, knowledge, systems, and acceptance scenarios.

For work that waits, runs asynchronously, or involves a person, ask about correlation, persisted state, task assignment and authorization, evidence shown, every decision outcome, deadlines, reminders, resumption, duplicate events, cancellation, recovery, audit, and status visibility.

Keep endpoints, payloads, node types, prompt text, and code out of functional SOPs.

## Round 4: experience design

Identify where modalities materially change behavior.

- For voice, discover target listeners and locales, telephony context, identity, brand/voice guidance, pronunciation needs, pace preferences, turn-taking, interruption, silence, recognition repair, confirmations, sensitive values, latency, transfer, disconnects, accessibility, and acceptance measures. Propose an initial design when the user has not prescribed one.
- For digital channels, discover capability differences, content formats, session/asynchronous behavior, identity, privacy, delivery failure, handoff, accessibility, and channel fallbacks.

Create only applicable experience documents and trace their requirements to use cases.

## Round 5: technical design

Begin technical category documents when functional scope is stable enough to make useful choices. Discover:

- product/component mapping, system context, trust boundaries, environments, state, workflow, model, prompt, tools, knowledge, and guardrails;
- connectivity, service identity, integration behavior, retries, idempotency, and recovery;
- API operations, request/response mappings, errors, authorization, and contract evidence;
- data classification, authorization, retention, privacy, security, and audit; and
- observability, support, testing, release, rollback, and post-release verification.

Use current evidence for platform-specific claims. Mark unavailable evidence `Not verifiable` rather than relying on memory.

## Round 6: reconcile and assess readiness

Cross-check the complete package:

- the index lists every document and matches its metadata;
- wave assignments and approved baselines do not conflict;
- every in-scope use case has SOP and acceptance coverage;
- experience requirements map to use cases;
- functional requirements have technical treatment or explicit blockers;
- integrations and APIs map to functional needs;
- shared facts have one canonical owner;
- open questions and dependencies have owners and next actions; and
- Wave 1 foundation and selected use case have evidence supporting the target.

Run the structural checker, then apply the semantic review and readiness guide. Ask only the questions that can materially improve the next verdict.
