# Evidence schema and source compatibility

## CLI and intake

`decompose_bot.py EXPORT [FRESH_OUTPUT]` preserves export-only usage. Optional repeatable `--additional-export`, `--botkit`, `--companion-source`, `--contracts` accept files/directories/ZIPs. Source groups use deterministic ordinal IDs (`source_001/...`) in argument order. A selected file does not implicitly authorize sibling files; selecting its folder/ZIP inventories all members. `--definition` selects exact manifest IDs, and `--all-definitions` explicitly selects every definition in export inputs. Unselected definitions stay visible. Companion-discovered definitions require selection as exports before capability analysis.

`--xo-version` preserves legacy versus XO 11 routing. `--scope goals-only`, `--defer`, `--universal` and `--parent-id` record scope/coordination decisions. Universal metadata (`isUniversal`, `childBots`) also enables planning; other architecture evidence requires the analyst to select the mode. No standalone parent is required.

Sources and output cannot overlap. Outputs must be empty/new. ZIP traversal, links, duplicate members and oversized inputs are rejected (20,000 members and 256 MiB per selected input). Directory symlinks are inventoried as unsupported, never followed. Unknown files remain in the manifest; only sanitized derived evidence is written. A successfully written partial ledger returns zero; unsafe intake returns nonzero. Parse success does not imply completeness.

## Version 2 compatibility

Plugin version 0.4.0 adds artifact/dependency coverage. Existing `dialogs`, `services`, `entities`, `scripts`, `forms`, `environment_references` and `subdialog_calls` remain in `_inventory.json`; schema version is now 2. Nodes and `used_in` include recursively expanded occurrences. `nodes_total` now counts expanded occurrences; `discovery.outer_nodes`, `physical_nodes`, `expanded_occurrences` and `component_definitions` distinguish denominators. Preserve original IDs and raw transitions; display names are not unique keys.

All dialog files, including hidden/support flows, use `dialog_####_<name>.md` to prevent name collisions. `_index.md` links them. Single-export evidence stays at output root. Multiple selected exports use `bot_###/`; root coverage spans the full selected system. Generated `_analysis_draft.md`, `_technical_reference_draft.md` and optional `_system_review_draft.md` are scaffolds requiring semantic completion. Existing consumers that assumed filtered system dialogs or old filenames must read the index and schema version.

## Coverage records

`_artifact_manifest.json` and `_coverage.json` retain logical source, source group, byte size, original hash, sanitized hash where parsed, role, parse/analysis status and exclusion reason. Original absolute paths are omitted. Source IDs may themselves contain identifying filenames; review them before sharing.

The coverage ledger adds:

| Collection | Evidence and limits |
|---|---|
| `bots` | Original ID/name, explicit version, parser route, artifact, dialog identities |
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

Gap categories include missing source, present but uninspected, unsupported parse, intentional exclusion, unresolved helper/reference/dynamic target, incompatible artifacts, unknown backend semantics, state ambiguity and unverified runtime binding. Supported statuses are open, deferred and resolved. Closure requires `resolution_evidence` and appended `resolution_history`; retain old facts and distinguish replacement decisions from supplied implementations.

## Semantic review and validation

For each `review_item`, replace the initial pending reason with a specific disposition/reason. Valid dispositions: analyzed, evidence-only (`evidence_only`), excluded by scope, external/unavailable, unresolved or unsupported (snake_case in JSON). Analyzed items need delivered `document_refs`; excluded items need `scope_decision`. Document refs are a final document filename plus optional literal anchor/marker present in that document. Generated source is evidence-only until reviewed, never automatically semantically analyzed.

The five `status` fields report parser execution, static document coverage, implementation dependencies, source-release compatibility and runtime validation independently. Preserve partial implementation when static gaps remain. Runtime status changes need separate `runtime_evidence`. Report reconciliation checks validate recorded accounting and links; they cannot prove the analyst's interpretation or an external service's behavior.

## Explicit unsupported boundaries

Supported graph expansion includes inline `nodes` and referenced component child `nodes` under action containers, with cycle/depth/occurrence bounds. Independent physical discovery flags unexpanded node records. Unknown types and references survive in warnings. Other graph schemas require targeted extension or declared unsupported review.

JavaScript analysis is lexical and dependency-free, not syntax-tree based. Function declarations/expressions/arrows/object methods, direct calls, literal registrations, exact state paths and common environment syntax seed review. Regex/template code, ES module/import alias resolution, computed properties/calls, control flow, registry-based/normalized/pattern dispatch, provider semantics and effective bindings are not mechanically proven. Read the sanitized source and record semantic conclusions; do not count candidate discovery as closure. Source contracts are inventoried but need endpoint/schema/version matching by the analyst.
