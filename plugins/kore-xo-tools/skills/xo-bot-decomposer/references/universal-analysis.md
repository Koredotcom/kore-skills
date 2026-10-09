# Universal and child-bot analysis

Use when supplied architecture, parent settings, registry or orchestration shows multiple bots operating as one conversation. Multiple unrelated export files alone do not prove a universal system. Parent behavior may be distributed across settings, a common initializer, BotKit and a registry; missing parent export/source must remain visible.

## Plan and work ownership

Refine `_system_plan.json` before delegating: parent identity where known, child IDs/names/version/hash, included capability slices, source groups, shared configuration/hooks/helpers, dependency candidates and deferred/excluded domains. Same names do not prove identity. Preserve source hash duplicates as copies with distinct provenance, and retain separately versioned implementations.

Assign child passes and a shared-runtime pass with the same selected manifest, ledger schema and status vocabulary. Workers use read-only sources and distinct output directories. Keep parser/tool edits under one coordinator. Use available authorized subagents, queue within concurrency limits, or perform identical sequential passes. Do not create new user-owned chats.

Each worker returns local documents plus this JSON handoff (arrays may be empty only with an explanation in quality/scope):

```json
{
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
python3 scripts/reconcile_system.py <output>/_coverage.json <new-system-ledger.json> <child-handoff.json> <shared-handoff.json>
```

The helper verifies source hashes/identities, deterministically merges handoffs, flags missing child work and same-label routing leads, and preserves global gaps. Input ordering is irrelevant; parallel and sequential passes use identical records. It deliberately does not certify the merged system. Review the resulting register and incorporate global findings into the main coverage ledger.

Perform a separate semantic pass over the **whole selected system**:

1. Map responsibility owners and consumers for initialization, verification, language/keypad, prefetch, announcements, reporting and handoff. Validate actual registry/dispatch semantics and target ownership.
2. Compare overlaps, independently versioned shared code/config, state keys/shapes, reset ordering, return/resume contracts and terminal suppression. Availability elsewhere does not repair wrong-owner dispatch.
3. Trace selected journeys across entry, identity/authorization, dispatch, child execution, shared hooks/services, errors/retries, interruptions/resumption and completion/transfer. Give every stage/edge a source owner and evidence, or a gap; do not fill unproven startup order with a happy path.
4. Reconcile each child's local gaps with global IDs. Keep shared dependencies open even when every child pass succeeds. Record any scope expansion or explicit replacement decision.

Journey records use `stages` containing `stage`, `owner`, `evidence` and optional `gap_id`; supported stages are `entry`, `identity_authorization`, `dispatch`, `child_execution`, `shared_hooks`, `errors_retries`, `interrupt_resume`, `completion_transfer`. Source-accounted stages still have unverified runtime bindings.

## Consolidated deliverable

The system review begins with the same current coverage warning as both main output types, then provides architecture/responsibility map, route/entry-return matrix, shared-state lifecycle, deduplicated integration/helper ledger, journey coverage, scope decisions and prioritized global gaps. Child, parent/shared-runtime and end-to-end statuses are explicit and independent. Keep child documents and references; a concatenation of them is not a system review. Verify source-release agreement based on specific target/schema/contract evidence, never version-number differences alone.
