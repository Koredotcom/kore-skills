# Universal and child-bot analysis

Use when supplied architecture, parent settings, registry or orchestration shows multiple bots operating as one conversation. Multiple unrelated export files alone do not prove a universal system. Parent behavior may be distributed across settings, a common initializer, BotKit and a registry; missing parent export/source must remain visible.

## Plan and work ownership

### Read the universal configuration

The extractor recognizes `type: "universalbot"` and `linkedBotsDetails`, as well as legacy `isUniversal`/`childBots` hints. A recognized parent may omit `dialogs`; local dialogs, when present, remain part of the parent work package. Do not infer a fallback or welcome binding from a hidden dialog's name.

`linkedBotsDetails` records supply `_id` and display names. Keep each occurrence, grouping repeated exact IDs for identity coverage while retaining all names and pointers. Match supplied definitions against their `_id`, `refId`, `botId`, `streamId` or `id`. Exported `_id`–`streamId` pairs in `fallbackDetails`/`inclusiveDetails` provide explicit aliases. Never strip prefixes or match display names. Overlapping aliases, duplicate export snapshots, malformed entries and unavailable/unselected child sources require reconciliation. These metadata lists are not task bodies or proof of runtime routing order.

The explicit exception is a user-authorized temporary name basis: pass `--linked-identity name` when registry IDs are defective. Group by exact nonempty registry names and select sources with the same exported bot name (top-level `name`/`botName` or `localeData.en.name`), not by filenames, partial names or case folding. Original IDs remain evidence, not rewritten values. Same-name/different-ID records and duplicate matching source snapshots remain ambiguous. Attach stream mappings only when both their name and registry ID agree with the named entry. An ID-only event owner shared by multiple named entries remains unresolved even if each named source is available. Task IDs/refIds are still resolved exactly inside the selected owner. Report registry entry count, distinct name count, distinct ID count and the selected grouping basis separately; none proves deployed bot count.

For each `botEvents` entry, preserve the complete configuration, including conditions, channel restrictions, scripts, messages, first-message options and telephony options. Normalize the enabled state and action. For `triggerDialog`, resolve `task` against the selected owner's dialog `_id` or `refId`; `linkedBotStreamId` selects the owner. An absent/null/empty linked owner permits only a parent-local lookup, with that basis recorded; it never authorizes choosing a child that happens to contain the task. An explicit parent identity is also local. Retain unresolved, ambiguous, dynamic or wrong-owner references as gaps. Disabled entries and `showMsg`/`runScript` actions retain stale task fields as configuration evidence without creating an active dialog route. Unknown actions remain unsupported review items.

Account separately for `INTENT_UNIDENTIFIED`, `ON_CONNECT_EVENT`, `WELCOME_MESSAGE_EVENT`, `TELEPHONY_WELCOME_EVENT` and any other exported events. Cross-reference `defaultDialogId` with a matching unidentified-intent event to find its configured owner; otherwise attempt only a local lookup and flag unverified ownership. Preserve disagreements between the default setting and enabled event target. A disabled matching event does not establish default activation. Do not invent precedence among connect, welcome, telephony and default settings: explain the exported configuration and identify the evidence needed for effective behavior.

Automatic dependency discovery stays inside supplied export inputs. An unambiguous parent can select exact linked sources there, including nested linked parents. Explicit `--definition` selection is authoritative and does not expand. Separate parent configuration/local-dialog work, selected child work, shared runtime and coordinator work. Missing linked exports remain `linked_source_dependencies`, not completed child packages.

Request missing named child exports and BotKit/helper source early, with a consolidated evidence-backed list. Registry discovery does not download linked definitions from XO or recover their implementations from the parent. Once supplied, analyze every linked child within the agreed system scope; keep missing/deferred children visible and finish the available portions. Do not ask again for a dependency already explicitly deferred unless new evidence changes the request.

### Analysis order

Begin with system-wide mechanical intake and a parent/shared-runtime semantic pass. Publish a common route/state contract and open dependency list for child passes. Analyze independent children concurrently when authorized, each with the same parent/shared evidence and separate outputs; use serial passes otherwise. Analyze strongly coupled or cyclic groups jointly rather than imposing a false dependency order. After child passes, reconcile ownership, initialization/reset behavior, handoff payloads, return/resume and terminal paths across the whole system. Revise affected passes when new shared evidence changes their assumptions. This staged approach preserves interdependencies without requiring every unrelated child to be analyzed serially.

Refine `_system_plan.json` before delegating: parent identity where known, child IDs/names/version/hash, included capability slices, source groups, shared configuration/hooks/helpers, dependency candidates and deferred/excluded domains. Same names do not prove identity. Preserve source hash duplicates as copies with distinct provenance, and retain separately versioned implementations.

Assign parent, child and shared-runtime passes with the same selected manifest, ledger schema and status vocabulary. Workers use read-only sources and distinct output directories. Keep parser/tool edits under one coordinator. Use available authorized subagents, queue within concurrency limits, or perform identical sequential passes. Do not create new user-owned chats.

Persist the current plan and each package's notes, progress and handoff in the [analysis workspace](analysis-workspace.md). Workers save small completed units to their assigned directory; the coordinator saves decisions, dependency requests, shared-contract revisions and checkpoints. On continuation, check recorded source/contract revisions and actual worker status before reassigning interrupted packages. Saved complete child outputs remain reusable when their dependencies are unchanged.

### Exclusive ownership and shared BotKit analysis

The coordinator is the sole dispatcher and shared-ledger writer. The generated plan assigns each selected bot definition to its parent/child package and non-definition companion sources to `shared_runtime`. Refine these assignments before dispatch: one owning package per artifact, including BotKit registrations, helpers and config. Treat identical source copies as a deduplication lead, not permission for independent workers to repeat the same semantic analysis. A tightly coupled group may own several bot definitions; remove those artifacts from their former packages rather than duplicating assignments. Parent routing and BotKit are coordinated baseline passes; child passes depend on both.

The shared-runtime owner analyzes the BotKit bundle once: bootstrap/registration, global hooks, component dispatch, helper chains, request/response consumers, state mutations, injected bot/task routes, callbacks, timeouts, retries and termination. Publish a source-linked contract with a revision, handler/route keys, consumers and known gaps. Use that contract in every child package, instead of giving each child a separate BotKit investigation. Missing BotKit still has one owner for tracking its unresolved requirements; do not invent a source identity or a handoff when no source exists.

Lock `ownership_policy.assignments_locked=true`, set `shared_contract_revision` and `shared_contract_refs`, and send workers their package ID, owned artifact IDs/hashes, capability slice, shared-contract snapshot, output directory and boundary rules. A baseline may explicitly contain gaps; locking it does not claim completeness. Workers may read assigned bot source and the common contract, but must not independently analyze unassigned bots or raw BotKit/helper sources, fetch more inputs, change ownership, launch subagents or edit the common ledger. They return requests to the coordinator. The coordinator forwards a question to the existing owner, merges the answer once, versions changed contracts and requests only affected workers to revisit their analysis. Do not start duplicate owners for the same dependency.

At a bot-to-bot or bot-to-BotKit boundary, preserve a structured dependency record rather than an empty placeholder: stable dependency ID, caller artifact/dialog/node and evidence, target bot/task or handler as exported, routing condition, input payload/state, expected response/callback, state changes visible to the caller, return/resume location, error/timeout/terminal expectations, assigned owner package and status. Unknown fields stay explicitly unknown. A child describes its side of the boundary and references the owner's implementation; it does not recursively decompose the destination. The coordinator closes `awaiting_owner_analysis` only by linking the target owner's evidence and checking the boundary contract. Unavailable source remains `missing_source`; incompatible or ambiguous routes stay unresolved. Final reports must contain linked explanations or explicit gaps, never unresolved placeholders presented as complete behavior.

Plan-aware reconciliation checks declared source ownership, source hashes, duplicate claims, missing owner handoffs and shared-contract revision. It does not enforce an operating-system sandbox, detect unreported reads, or prove semantic accuracy. Keep worker prompts/tools scoped and inspect their returned artifacts as well as running the check.

Each worker returns local documents plus this JSON handoff (arrays may be empty only with an explanation in quality/scope):

```json
{
  "work_package_id": "child_001",
  "analyzed_artifacts": [{"artifact_id": "source_001/botDefinition.json", "source_hash": "<manifest hash>"}],
  "shared_contract_revision": "baseline-1",
  "source_identity": {"artifact_id": "source_001/botDefinition.json", "source_hash": "<manifest hash>", "bot_id": "<original bot ID>"},
  "capability_scope": "Selected outcomes and explicit exclusions",
  "goals_events": [{"name": "Example outcome", "source": "<evidence>", "classification": "goal or event", "quality": "partial"}],
  "entry_assumptions": [],
  "routes_returns": [],
  "state_contracts": [],
  "dependencies": [],
  "exclusions": [],
  "gap_ids": [],
  "quality": {"static": "partial", "runtime": "not_established"},
  "journeys": []
}
```

Routes include caller, target owner/identifier, comparison, condition, payload/state, return/terminal handshake and evidence/gap. State contracts include producer/consumer, initializer/reset/lifetime, exact fields and unresolved aliases. Dependencies include helper/hook/provider/parent sources and missing contracts. A shared-runtime handoff uses its registered manifest artifact identity and identifies the additional shared files in dependencies. Never invent absent fields to satisfy a schema.

## Coordinator reconciliation

```bash
python3 scripts/reconcile_system.py <output>/_coverage.json <new-system-ledger.json> <parent-handoff.json> <child-handoff.json> <shared-handoff.json> --plan <output>/_system_plan.json
```

The helper verifies source hashes/identities, deterministically merges separate parent/child/shared handoffs, flags missing source passes and same-label routing leads, and preserves global gaps, registry dependencies and event targets. Input ordering is irrelevant; parallel and sequential passes use identical records. It deliberately does not certify the merged system. Review the resulting register and incorporate global findings into the main coverage ledger.

Use `--plan` for coordinated subagent runs. List every owned source actually inspected in `analyzed_artifacts`; shared-contract consumption belongs in dependency references, not a claim to have reanalyzed its raw sources. A package can return one handoff covering several assigned sources. Missing claimed coverage remains a gap. Empty-source packages need no fabricated handoff. Legacy handoffs without a plan remain readable, but report `ownership_validation=not_checked_legacy_handoffs` and do not establish exclusive ownership.

Perform a separate semantic pass over the **whole selected system**:

1. Map responsibility owners and consumers for initialization, verification, language/keypad, prefetch, announcements, reporting and handoff. Validate actual registry/dispatch semantics and target ownership.
2. Compare overlaps, independently versioned shared code/config, state keys/shapes, reset ordering, return/resume contracts and terminal suppression. Availability elsewhere does not repair wrong-owner dispatch.
3. Trace selected journeys across entry, identity/authorization, dispatch, child execution, shared hooks/services, errors/retries, interruptions/resumption and completion/transfer. Give every stage/edge a source owner and evidence, or a gap; do not fill unproven startup order with a happy path.
4. Reconcile each child's local gaps with global IDs. Keep shared dependencies open even when every child pass succeeds. Record any scope expansion or explicit replacement decision.

Journey records use `stages` containing `stage`, `owner`, `evidence` and optional `gap_id`; supported stages are `entry`, `identity_authorization`, `dispatch`, `child_execution`, `shared_hooks`, `errors_retries`, `interrupt_resume`, `completion_transfer`. Source-accounted stages still have unverified runtime bindings.

## Consolidated deliverable

The system review begins with the same current coverage warning as both main output types, then provides architecture/responsibility map, route/entry-return matrix, shared-state lifecycle, deduplicated integration/helper ledger, journey coverage, scope decisions and prioritized global gaps. Child, parent/shared-runtime and end-to-end statuses are explicit and independent. Keep child documents and references; a concatenation of them is not a system review. Verify source-release agreement based on specific target/schema/contract evidence, never version-number differences alone.
