---
name: xo-bot-decomposer
description: Analyze Kore.ai XO bot exports and supplied companion code into business goals, technical references and explicit coverage gaps. Use for single-bot or universal/child-bot flows, events, integrations, SDK webhooks, BotKit and helper dependencies. Do not estimate effort or implement a replacement.
---

# XO Bot Decomposer

Produce two evidence-based documents, `<bot_slug>_analysis.md` and `<bot_slug>_technical_reference.md`, plus a sanitized dependency/coverage register. For universal systems, also produce child reports and `<system_slug>_system_review.md` reconciling the selected end-to-end journeys. Source discovery, semantic document coverage, implementation closure, source-release alignment and runtime validation are separate results. A useful partial report must retain unresolved dependencies prominently.

## Protect inputs and preserve scope

Use only supplied or authorized artifacts. Keep originals unchanged and generated evidence outside the plugin/source directories. Never execute supplied applications, install their dependencies, fetch vendor scripts or call integrations to infer behavior. Syntax checks, if requested, do not establish behavior. Do not commit exports or generated reports.

Redaction covers common credentials in JSON, config, helper/hook code, scripts and URLs, including fields marked `isSecured=false`. It is not a privacy guarantee. Inspect all deliverables for credentials and identifying examples; preserve credential references and source identities while masking literal values. Record original and sanitized hashes separately. Never restore redacted values. Unsupported artifacts remain in the manifest and are not copied into outputs.

Accept an export JSON, ZIP, extracted folder, or explicitly selected set of exports. Accept optional companion JavaScript/configuration, BotKit source, deployment descriptions and provider contracts. A directly selected JSON authorizes that file; select its enclosing export folder/ZIP or pass companion files explicitly to include siblings. Discover candidate dependencies within the authorized source boundary; do not automatically analyze unrelated domains or expand migration scope. A needed task found in another child closes availability only, not dispatch ownership or state compatibility.

Use an explicit destination without asking again. Otherwise create fresh temporary evidence and save final documents in the current working directory unless that would be ambiguous or overwrite user files. Ask only for material missing inputs or decisions; continue independent work. If unavailable or deferred, finish partial reports with the gap intact. Silence is not an approved exclusion.

## Generate mechanical evidence

```bash
python3 "${PLUGIN_ROOT}/skills/xo-bot-decomposer/scripts/decompose_bot.py" \
  "<export.zip-or-json-or-folder>" "<fresh-output-directory>"
```

When testing source with `PLUGIN_ROOT` unset, resolve scripts relative to this file. Python 3.10+ is sufficient; no third-party runtime packages are required. Read [references/evidence-schema.md](references/evidence-schema.md) for arguments, supported shapes, schema migration, statuses and helper limitations.

- Repeat `--additional-export`, `--botkit`, `--companion-source` and `--contracts` for selected inputs. Pass `--defer <dependency>` for unavailable inputs already identified.
- Multiple plausible definitions produce an explicit selection gap. Inspect `_artifact_manifest.json`, then rerun to a fresh output with repeated `--definition <exact-artifact-id>` or explicit `--all-definitions`. Do not choose the largest definition silently.
- Explicit version metadata or `--xo-version` selects the route; XO 10 includes earlier releases, XO 11 is a compatible parsing route, not a guarantee about later schemas. Preserve product version, parser route and companion release identity separately.
- `--scope goals-only` still discovers all structural dependencies and quantifies excluded support detail. `--universal --parent-id <known-id>` creates a coordinated analysis plan; omit parent ID when unknown. Enable universal analysis whenever architecture, registry or routing evidence establishes an umbrella system, even without a standalone parent export.

Read `_coverage.md`, `_artifact_manifest.json`, `_inventory.md`, `_index.md` and `_metadata.md` first. Multi-export runs keep per-export evidence in `bot_###/`. Use `_coverage.json` for cross-source records and `_inventory.json` for legacy service/entity/script/form collections plus recursive occurrences. The generated `*_draft.md` files are boundary scaffolds, not completed semantic reports.

## Analyze behavior and close only supported gaps

Read [references/implementation-analysis.md](references/implementation-analysis.md) when executable companions, hooks, event logic or routing dependencies occur. The scanner uses bounded lexical analysis, not a JavaScript AST. Names, registrations and calls are candidates, not proof of execution. Inspect actual bootstrap, imports, guards, dispatcher and reachable project helpers before classifying a hook as active or matching a webhook. Unsupported variants remain explicit gaps.

Account for every artifact, component, recursive node occurrence, dialog, event, helper and hook in `review_items`. Analyze known types and preserve unsupported/null/cyclic references. Keep node IDs, component IDs, parent chains, original pointers and expanded use sites. A shared component is one definition with many occurrences. Preserve raw conditions and boolean nesting; do not invent missing operators or collapse duplicate display names.

Classify lifecycle/support behavior separately from user goals, but retain its technical implementation. Event-driven identity, initialization, fallback, hidden recovery and transfer can be the principal capability of a bot. Read event configuration, enabled state and target IDs; names and missing incoming edges are only clues. Zero native transfer nodes does not mean no scripted, VXML or external handoff.

A dialog may contain multiple business outcomes. Inline a sub-dialog with one parent; describe shared sub-flows once with every caller. Treat it as a separate goal only when independently invokable with its own outcome. Name goals with plain verb–noun phrases. Keep business steps free of URLs, payloads, code and platform identifiers; express decisions, validation, actions, errors and escalation from evidence.

For 50+ candidates, ask which goals need expanded prose after the summary. Structural discovery, event/helper/hook inventory, dependency reconciliation and early warnings still cover the whole selected source set.

## Universal system coordination

Before child passes, read [references/universal-analysis.md](references/universal-analysis.md). Refine `_system_plan.json` with selected capabilities, identities/hashes, versions, shared responsibilities, deferred inputs and output ownership. Use independent child and shared-runtime subagents when available and permitted by active instructions; otherwise perform equivalent sequential passes. Respect concurrency limits and give each worker a separate output directory. One owner controls shared tooling.

Require structured handoffs using the linked schema. Reconcile them with `scripts/reconcile_system.py`, then perform a separate coordinator analysis of dispatch ownership, shared state, initializer ordering, overlaps, errors, interruption/resumption and terminal/return paths. A mechanical merge or successful child report is not universal completion. Trace selected journeys and report child, shared-runtime and end-to-end coverage separately.

## Write and validate reports

Read [references/output-detail.md](references/output-detail.md) before authoring. Put **Coverage and missing inputs** immediately below each title, before metadata, counts or goal tables. Generate the same warning from the current `_coverage.json` for business, technical and system reports. It states inspected artifacts, requested boundary, statuses, affected behavior, practical consequence, next evidence and ledger link. Keep deferred, excluded, unsupported, ownership-mismatched and runtime-unknown items visible. Describe SearchAI/SmartAssist/Agent Assist according to supplied evidence: absent, referenced without implementation, uninspected or intentionally excluded; never use an unconditional export disclaimer.

Update each review item's disposition, specific reason and document references. Resolve a gap only with `resolution_evidence` and an appended `resolution_history`; finding a client/helper does not close provider/runtime questions. Record semantic additions (e.g. exact dispatcher matches, missing reset paths or state-key mismatches) in the same ledger. Do not change counts to hide unknown categories.

```bash
python3 "${PLUGIN_ROOT}/skills/xo-bot-decomposer/scripts/review_coverage.py" \
  "<output>/_coverage.json" --render-warning "<output>/coverage_warning.md"
# Insert this current warning immediately below each report title, then validate:
python3 "${PLUGIN_ROOT}/skills/xo-bot-decomposer/scripts/review_coverage.py" \
  "<output>/_coverage.json" --business "<analysis.md>" --technical "<technical_reference.md>"
# Universal mode also requires --system-review "<system_review.md>".
```

The validator checks disposition/count accounting, evidence for recorded closures, document references and exact shared-warning placement. It does not certify source truth, semantic correctness or runtime behavior. Review all branches, dependencies, callback/error continuations and privacy separately. Deliver useful partial outputs; report parser success independently from unresolved analysis. Link local files, identify parser routes, summarize material gaps and name any untested installed/live behavior.

## Offer an optional storage handoff

After validation, provide local links and offer a choice: **local files only**, **Google Drive** (My Drive or a shared drive), **OneDrive**, or **SharePoint**. Recommend `<Bot Name> - XO Decomposition` as the upload-folder name, while allowing another name or an existing folder. Honor prior choices without asking again; selecting a local output folder does not authorize upload.

For an accepted upload:

1. Discover the selected provider's available connector tools and guidance. Google Drive uses the `google-drive` skill; OneDrive and SharePoint use their available connector guidance. Verify browsing, upload, readback, and new-folder creation capabilities as needed. These are destination options, not a promise that every environment has the connectors. If a connector or write access is unavailable, explain the limitation and supply the local files for manual upload. Do not require cloud access to finish the documents or substitute a different provider without agreement.
2. Let the user provide a folder URL/ID or choose from accessible folders when browsing is supported. Show names, locations, and links to resolve ambiguity. For OneDrive, resolve the account and drive; for SharePoint, resolve the site, document library, and folder; for Google Drive, resolve My Drive or the shared drive. Ask only for missing details; do not depend on a native folder picker.
3. Keep the final documents and their referenced sanitized coverage register in one folder. For a new folder, confirm the parent and use the recommended name or the user's alternative. Accepting this choice authorizes creation without another confirmation. Reuse an explicitly chosen existing folder directly. If the user selects a drive or document-library root, create the named folder under it instead of uploading loose files there.
4. Check for an exact-name folder before creating one. Offer reuse or a distinct name such as `<Bot Name> - XO Decomposition - <YYYY-MM-DD>` if it exists. Verify the resolved folder identifier and write access. Preserve sharing settings, and resolve existing filename collisions according to the user's preference before overwriting files.
5. Upload only the final reports and explicitly approved sanitized coverage/reference deliverables, preserving relative links, contents and filenames; exclude source exports and intermediate evidence. Include child/system reports only within the accepted handoff scope. Convert only when requested, using applicable document/provider guidance and verifying the converted files first.
6. Verify every selected file and its parent folder through connector readback and return observed folder and file links. Report partial success accurately. Before retrying an uncertain upload, check whether it already created a file and retry only missing or failed uploads.
