# Decomposition document detail

Read before writing final reports. Evidence inventory supports interpretation; it does not replace semantic analysis.

## Shared opening and coverage

Both reports and any universal-system review start with their title followed immediately by the current warning generated from `_coverage.json`. Metadata and goal tables follow it. Preserve identical gap IDs, statuses and counts. Add concise business-language impact beneath the warning when needed. Keep top-level warnings visible even when full code is in a linked companion reference.

Use separate fields for parser execution, static document coverage, implementation dependency closure, source-release compatibility and runtime validation. Record no-blocker conclusions only within the inspected boundary after review. Do not infer no external hooks from zero webhook nodes. Configured/exported values are not effective deployment evidence. A deferred input remains open until supplied or explicitly replaced/excluded, with its consequence retained.

## Business goal decomposition

After coverage, provide source/parser route, analysis date and companion-reference links; then:

1. Goal summary mapping outcomes to source dialogs; mark inferred goals and overlapping routes.
2. Events/support table for actual initialization, identity, welcome, fallback, follow-up, completion, recovery and transfer bindings. An event-only bot may have zero user goals.
3. Languages/channels with enabled state, digital forms with associated goals, and global/local PII configuration. Absence in an export is not absence in production.
4. Goal details: trigger evidence and numbered steps covering collection, clarification, validation, decisions, services, confirmations, failures and escalation. Link dependencies and shared implementation responsibilities without dumping code or identifiers.
5. Shared sub-flows, described once with callers; inline single-parent flows. Do not duplicate independently invokable goals.

Forms are presented as forms, not invented conversational collection. Keep steps as detailed as the evidence supports; there is no minimum step count. A limited expanded-goal selection does not reduce dependency discovery.

## Technical reference

Group by responsibility and link every implementation to its goals/events and stable evidence IDs. Include relevant support/hidden paths; no blanket exclusions based on classification.

- **Integration/configuration provenance:** exported defaults, companion definitions, deployment override sources, environment references, known units and effective-value uncertainty. Describe authentication by references/profile/header names; missing credentials do not imply unauthenticated access.
- **Services:** method, sanitized URL, headers/body, processors, consumer response fields, provided schemas/fixtures, error/timeout/retry/cancellation and continuation. Distinguish client expectations from verified provider contracts.
- **SDK webhooks:** definition and use-site counts, owners/parents, input/output state, event/dispatcher, matched handler and matching evidence, node/handler timeouts with unknown units preserved, callback/error flow, backend and registration gaps. Several names may share one generic callback.
- **Events/support:** initialization and reset order, event targets/enabled state, hidden recovery, completion/fallback, actual transfer stages. Preserve `AgentTransfer` action, `Transfer` event and conversational `Agent Transfer` as distinct identities until binding evidence resolves them.
- **BotKit hooks:** actual registration/bootstrap, bot identity, project handler, feature guards, ordering, NLP/text mutation, state effects, external calls, route injection, forwarding/callbacks, interruption/resume and failure. Label pass-through, inactive sample, imported-only, unsupported and runtime-unverified separately.
- **Helpers/executable content:** signatures, source/decoded line, sanitized implementation, callers/callees, external calls and purpose. Include sibling functions, entity/message/retry callbacks and service processors. Deduplicate implementation prose while retaining each call context; uncalled definitions are not active goals.
- **Entities/forms:** type, values/format, prompts, validation/retry behavior and relevant field evidence.
- **State and routes:** focused producer/consumer table with initializer, initial/reset value, replacement behavior, persistence, failure/terminal flags, exact case, aliases and unresolved dynamic paths; route/entry-return table with actual comparison semantics, owner, payload/state, resume handshake and source-release gaps.

Full code may live in a sanitized evidence appendix; each responsibility needs a semantic explanation and links. Do not link unavailable files. Keep raw hashes and sanitized hashes distinct. Include only execution-relevant NLU/channel/state facts, avoiding indiscriminate configuration dumps.

## Quality gates

Compare independent discovery totals with parsing/expansion, then reconcile every review item against the final documents. Relevant unsupported artifacts and types remain in the denominator. Every omission needs a disposition/reason; exclusions need a recorded user scope decision. Linked reference documents must be delivered or included in the agreed handoff.

Confirm that exact branches, duplicate names, repeated uses, errors, configuration and callback contracts remain intact. Resolve webhook/helper matches from dispatcher/bootstrap evidence; do not treat lexical candidate counts as analyzed coverage. Run `review_coverage.py` and a semantic/privacy review. A successful syntax/parser/document check is never runtime acceptance.
