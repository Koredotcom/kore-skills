# Evidence schema and source compatibility

## CLI and intake

`decompose_bot.py EXPORT FRESH_OUTPUT` accepts a standalone export without companions. Since plugin 0.6.0 the output argument is required; choose a fresh persistent evidence run inside the [analysis workspace](analysis-workspace.md), rather than relying on the former temporary default. Optional repeatable `--additional-export`, `--botkit`, `--companion-source`, `--contracts` accept files/directories/ZIPs. Source groups use deterministic ordinal IDs (`source_001/...`) in argument order. A selected file does not implicitly authorize sibling files; selecting its folder/ZIP inventories all members. `--definition` selects exact manifest IDs, and `--all-definitions` explicitly selects every definition in export inputs. Unselected definitions stay visible. Companion-discovered definitions require selection as exports before capability analysis.

`--xo-version` preserves legacy versus XO 11 routing. `--scope goals-only`, `--defer`, `--universal` and `--parent-id` record scope/coordination decisions. Universal metadata (`type: "universalbot"`, `linkedBotsDetails`, `isUniversal`, `childBots`) also enables planning; other architecture evidence requires the analyst to select the mode. No standalone parent is required. Recognized universal parents may omit `dialogs`, including inside the existing `botDefinition`/`appDefinition`/`app`/`bot` wrappers; invalid present dialog/component collections remain unsupported.

Without explicit selection flags, a source group containing one definition selects it; a group containing multiple definitions with exactly one universal parent selects that parent as a seed. Exact linked identities and evidence-backed stream aliases then select unambiguous dependencies among supplied export inputs, recursively. No sibling outside those inputs is read, unrelated definitions stay unselected, and multiple root candidates require selection. Explicit `--definition` overrides automatic expansion. Duplicate source matches are not silently picked.

`--linked-identity name` is an explicit, temporary alternative for user-confirmed bad IDs. It groups and discovers linked sources by exact exported bot names; the default remains `id`. The ledger and system plan retain `linked_identity_mode`; linked records retain `identity_mode`, `identity_key`, original `registry_id_values` and identity evidence. `universal_discovery` separately counts raw entries, distinct IDs, distinct names and groups under the chosen basis. ID/name inconsistencies produce `registry_identity_disagreement`; names never repair an ambiguous ID-only event route automatically. This option does not change task ID/refId matching, silently select duplicate-name exports or fetch external sources.

Universal `_system_plan.json` also declares `owned_artifact_ids` and `depends_on` per work package. Its draft `ownership_policy` forbids independent worker scope expansion/delegation and names the coordinator as shared-ledger writer. The coordinator publishes shared-contract references/revision and locks assignments before accepting delegated results. `reconcile_system.py --plan` checks handoff `work_package_id`, `analyzed_artifacts` IDs/hashes and `shared_contract_revision`, rejects overlapping assignments/out-of-scope claims, and exposes missing assigned-source handoffs. This checks declared work, not filesystem isolation or semantic correctness; see [universal-analysis.md](universal-analysis.md).

Outputs must be empty/new. A fresh evidence run may live inside a helper-initialized analysis subfolder within the supplied export folder; all marked analysis workspaces are pruned from discovery, and their relative paths are recorded in `intake_exclusions`. Generated workspace files cannot be selected as source inputs. Other source/output overlap remains rejected. ZIP traversal, links, duplicate members and oversized inputs are rejected (20,000 members and 256 MiB per selected input). Directory symlinks are inventoried as unsupported, never followed. Unknown files remain in the manifest; only sanitized derived evidence is written. A successfully written partial ledger returns zero; unsafe intake returns nonzero. Parse success does not imply completeness.

## Version 2 compatibility

Plugin version 0.4.0 adds artifact/dependency coverage. Existing `dialogs`, `services`, `entities`, `scripts`, `forms`, `environment_references` and `subdialog_calls` remain in `_inventory.json`; schema version is now 2. Nodes and `used_in` include recursively expanded occurrences. `nodes_total` now counts expanded occurrences; `discovery.outer_nodes`, `physical_nodes`, `expanded_occurrences` and `component_definitions` distinguish denominators. Preserve original IDs and raw transitions; display names are not unique keys.

Plugin version 0.5.0 adds universal registry/event collections without removing schema-2 fields. Bot/dialog `ref_id` and bot `identity_aliases` preserve identity namespaces; parent names can come from `localeData.en.name`. `universal_discovery` records independent registry, linked-identity, configured-event and default-setting denominators. `review_coverage.py` validates these against normalized records, even if record counts were edited. Earlier schema-2 ledgers remain accepted. `event_bindings` are also referenced in `events`; do not sum the two collections as separate events.

All dialog files, including hidden/support flows, use `dialog_####_<name>.md` to prevent name collisions. `_index.md` links them. Single-export evidence stays at output root. Multiple selected exports use `bot_###/`; root coverage spans the full selected system. Generated `_analysis_draft.md`, `_technical_reference_draft.md` and optional `_system_review_draft.md` are scaffolds requiring semantic completion. Existing consumers that assumed filtered system dialogs or old filenames must read the index and schema version.

## Coverage records

`_artifact_manifest.json` and `_coverage.json` retain logical source, source group, byte size, original hash, sanitized hash where parsed, role, parse/analysis status and exclusion reason. Original absolute paths are omitted. Source IDs may themselves contain identifying filenames; review them before sharing.

The coverage ledger adds:

| Collection | Evidence and limits |
|---|---|
| `bots` | Original ID/name, explicit version, parser route, artifact, dialog identities |
| `universal_parents` | Parent configuration, original type, registry settings, stream mappings and parent-local dialog IDs |
| `registry_entries`, `linked_bots` | Every linked registry occurrence plus grouped exact IDs, names, aliases/pointers, selected/unselected source candidates and resolution status |
| `event_bindings` | Complete `botEvents` configuration and default-dialog cross-reference, enabled/action/owner/task, exact ID/refId resolution, competing candidates and runtime uncertainty |
| `component_definitions` | Original definition and all expanded occurrence IDs |
| `node_occurrences` | Dialog/node/component IDs, parent chain, actual pointer, expanded path, raw transitions and sanitized source bodies |
| `webhooks` | Definition, exact occurrences/owners, timeout value/unit, parameters, continuations, handler candidates and independent backend/runtime status |
| `events` | Typed configuration containers, binding candidates, hidden support paths and script/markup transfer candidates; separate binding/container counts prevent treating all event evidence records as distinct active events |
| `bot_functions`, `calls` | Lexical signatures, decoded source lines, bodies, callers/callees and scoped definition candidates; imports/dynamic forms unresolved |
| `botkit_hooks`, `registrations` | Literal hook/registration candidates and bot ID where supported; no assertion of active deployment |
| `configuration` | Direct/template/bracket references, exported containers, companion definition layers; effective values unknown |
| `state_contracts` | Lexical exact paths, read/write/replace candidates, dynamic paths and reset/lifetime uncertainty |
| `routing_dependencies` | Exact dialog-ID links and literal SDK-like call candidates; actual signatures/owner/return semantics may require review |
| `executable_evidence` | Sanitized code and lexical limitations, including inline/processor/retry fields |
| `coverage_gaps` | Stable ID, category, severity, source evidence, affected behavior, consequence, next input, status/decision and resolution history |
| `review_items` | Independent accounting of files, components, occurrences, dialogs, code, imports, events, helpers and hooks |

Gap categories include missing source, present but uninspected, unsupported parse, intentional exclusion, unresolved helper/reference/dynamic target, incompatible artifacts, unknown backend semantics, state ambiguity and unverified runtime binding. Universal additions include `unresolved_linked_bot`, `unresolved_event_target`, `unverified_event_setting` and `configuration_disagreement`. Supported gap statuses are open, deferred and resolved. Closure requires `resolution_evidence` and appended `resolution_history`; retain old facts and distinguish replacement decisions from supplied implementations.

Universal source statuses distinguish `matched_source`, `missing_source`, `source_unselected`, `ambiguous_source`, `ambiguous_registry_identity`, `self_reference` and `unresolved_identity`. Event-target statuses additionally distinguish local/linked owner scope, missing/ambiguous owner or task sources, wrong-owner task availability, unsupported references/actions, `disabled`, `non_dialog_action` and unverified default ownership/activation. `matched_source` establishes one static source target only. All runtime bindings remain unverified. See [universal-analysis.md](universal-analysis.md) for interpretation and default/event precedence limits.

## Semantic review and validation

For each `review_item`, replace the initial pending reason with a specific disposition/reason. Valid dispositions: analyzed, evidence-only (`evidence_only`), excluded by scope, external/unavailable, unresolved or unsupported (snake_case in JSON). Analyzed items need delivered `document_refs`; excluded items need `scope_decision`. Document refs are a final document filename plus optional literal anchor/marker present in that document. Generated source is evidence-only until reviewed, never automatically semantically analyzed.

The five `status` fields report parser execution, static document coverage, implementation dependencies, source-release compatibility and runtime validation independently. Preserve partial implementation when static gaps remain. Runtime status changes need separate `runtime_evidence`. Report reconciliation checks validate recorded accounting and links; they cannot prove the analyst's interpretation or an external service's behavior.

## Explicit unsupported boundaries

Supported graph expansion includes inline `nodes` and referenced component child `nodes` under action containers, with cycle/depth/occurrence bounds. Independent physical discovery flags unexpanded node records. Unknown types and references survive in warnings. Other graph schemas require targeted extension or declared unsupported review.

JavaScript analysis is lexical and dependency-free, not syntax-tree based. Function declarations/expressions/arrows/object methods, direct calls, literal registrations, exact state paths and common environment syntax seed review. Regex/template code, ES module/import alias resolution, computed properties/calls, control flow, registry-based/normalized/pattern dispatch, provider semantics and effective bindings are not mechanically proven. Read the sanitized source and record semantic conclusions; do not count candidate discovery as closure. Source contracts are inventoried but need endpoint/schema/version matching by the analyst.
