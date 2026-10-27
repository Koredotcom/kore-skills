# Durable analysis and continuation

Use a persistent local workspace for every analysis, including single bots. Honor an existing destination; otherwise use `xo-analysis/` within the supplied export folder, or beside a supplied JSON/ZIP file. A universal system shares one workspace in the supplied parent/child export collection folder. Keep originals in place. Reuse the existing workspace to continue the same analysis; use a distinct descriptive name for an explicitly separate analysis, and ask only when the source location or scope is ambiguous. Never place generated analysis in the installed plugin directory or commit it to a source repository. Never put the only evidence, notes or handoffs in an OS temporary folder. This stores saved analysis, not an agent's hidden reasoning or a guarantee against disk loss. Do not promise recovery beyond the last saved work/checkpoint. Existing cloud-upload consent rules remain separate.

## Initialize and intake

Resolve helpers from the skill's scripts directory:

```bash
python3 scripts/analysis_workspace.py init "<exports-folder>/xo-analysis"
python3 scripts/decompose_bot.py "<exports-folder>" "<exports-folder>/xo-analysis/evidence/run-001"
# Add the selected companion/identity/scope arguments as usual.
```

For a selected JSON/ZIP, pass that original file as the input and place `xo-analysis/` in its containing folder. Select other ZIPs explicitly with `--additional-export`; scanning an enclosing folder does not recursively unpack nested ZIPs.

The intake output is now required: standalone runs cannot silently use temporary evidence. Temporary ZIP extraction remains disposable; original exports stay unchanged and derived evidence is persisted. The workspace helper refuses a nonempty destination or symlinked workspace. Use the real resolved location when the filesystem has a symlinked ancestor.

```text
exports-folder/
  original-export.json-or-zip      # unchanged; may also be parent/child export folders
  xo-analysis/                    # the analysis workspace
    ...                           # contents expanded below

xo-analysis/
  .xo-analysis-workspace.json      # intake exclusion marker; retain it
  README.md
  session.json                    # coordinator's durable resume index
  evidence/
    run-001/                      # immutable intake, manifest, inventories, initial ledger/plan
    run-002/                      # new inputs or parser changes; earlier evidence retained
  work/
    _coverage.json                # reviewed working ledger
    _system_plan.json             # current ownership plan, when universal
    parents/<package>/            # notes, progress.json, drafts, handoff.json
    children/<package>/
    shared_runtime/               # versioned BotKit contracts and findings
    system_review/                # dependency reconciliation and journey notes
  reports/                        # final/partial reports and required referenced registers
  checkpoints/
    CP-0001/
      session.json
      manifest.json               # hashes of evidence and saved working files
      files/work/                 # recoverable copies of saved work
      files/reports/
```

Intake prunes directories carrying the helper-created `.xo-analysis-workspace.json` marker before reading or counting their contents. `_coverage.json.intake_exclusions` records the skipped workspace paths. This applies to earlier runs and checkpoints as well as the current run; ordinary source folders named `analysis` or `xo-analysis` are not skipped merely because of their name. Never place original exports inside the marked workspace. Selecting generated files as source inputs is rejected. Nested output is allowed only as a fresh direct child of the initialized workspace’s `evidence/` directory; arbitrary source/output overlap remains rejected. Keep the marker when moving the workspace.

After intake, copy the initial ledger and applicable system plan into `work/`; keep the evidence originals immutable. Set package output directories under `work/` and retain source pointers/manifest IDs. These copied files are the canonical working records; do not alternate edits between their evidence originals and working copies. For a single bot, create one package in `work/children/` with the same progress/handoff rules, without inventing a universal architecture. Before delivery, place the current coverage register/manifest and referenced documents alongside reports or fix their relative links, then run report validation there.

Update `session.json` with the selected scope, identity mode, active evidence run, ordered intake inputs/options, durable original-source locations and hashes, package IDs/statuses/output paths, shared-contract revision, user decisions, missing/deferred inputs and concrete next actions. Original source locations may be private; this local index is not a public deliverable. Artifact IDs are stable only within an intake: after adding/reordering inputs, map old/new identities by provenance and source hashes rather than reusing ordinal source IDs blindly.

Each `source_locations` entry uses `path` (an absolute, resolved original file/ZIP path) and `sha256` (its lowercase original SHA-256 digest). For folder inputs, register the selected source files individually; do not use a sanitized hash or a temporary ZIP extraction path. `status` checks these records for changed/missing/unreadable originals; an empty list explicitly means no sources are registered yet. Keep private source locations in the local session, not the final reports.

## Save progress as work proceeds

The coordinator alone writes `session.json`, checkpoints and common ledgers. Each worker writes only its assigned package directory. Save notes and extracted facts with source references after each dialog/handler or coherent small unit, rather than waiting until the entire child finishes. Maintain each package's `progress.json`: assignment/source hashes, shared-contract revision used, completed and pending items, open dependency IDs, draft/handoff paths, status and next action. Save user answers, scope decisions and dependency requests to files as soon as accepted; chat history is not the system of record.

Checkpoint after intake, each completed package, shared-contract revisions, coordinator merges and before yielding a long-running analysis. Quiesce worker file writes briefly; checkpoint only consistent saved state:

```bash
python3 scripts/analysis_workspace.py checkpoint <analysis-folder> --note "Shared contract baseline and two child passes saved"
python3 scripts/analysis_workspace.py status <analysis-folder>
```

The checkpoint snapshots working files, reports and session state, and hashes retained immutable evidence runs. It does not copy raw exports or repeatedly duplicate large evidence runs. Previous checkpoints are not overwritten. Detected concurrent edits abort the snapshot; stop writers and retry. A process interruption before the session pointer updates can leave a valid newer checkpoint; `status` reports such orphan checkpoints for coordinator inspection. Incomplete `.pending-*` directories are not valid checkpoints. Keep this folder on durable storage; backups and disk availability remain the user's storage responsibility.

## Resume from the folder

Read the workspace README/session, run `status`, then read the current working ledger, ownership plan, shared contracts and package progress/handoffs. Inspect changed/missing files and checkpoint integrity before choosing the latest saved state. Verify original-source hashes at recorded locations; request missing or changed sources, preserving previously completed evidence and explicit gaps. A matching checkpoint confirms file consistency, not semantic completeness.

Continue from recorded next actions, reusing completed package outputs that match current source hashes, scope and shared-contract revision. Old agent IDs are not evidence that a worker is still running: check the current host, stop or join any existing worker before assigning its package again, and mark interrupted work for continuation rather than dispatching a duplicate. Give replacement workers the same assignment plus its saved progress, drafts and dependency records. Do not rerun intake into an existing evidence directory or overwrite completed reports merely to restart.

If inputs change, create the next numbered evidence run and keep its predecessor. Reconcile added/changed/missing sources and invalidate only affected packages and dependent contracts/journeys. Revise source IDs in ownership plans and handoffs explicitly. New BotKit evidence may require revisiting previously partial child consumers, not discarding unrelated completed analysis.

If working files are lost or damaged, compare the checkpoint's manifest and snapshots, then restore selected copies to a new recovery directory first. Preserve any newer work until reviewed; never automatically replace it with an older snapshot. Evidence runs are referenced by hash and retained in place; if evidence itself is missing, recover it from durable storage or re-extract from matching original sources into a new run and reconcile. Record recovery decisions and save a new checkpoint. Final continuation instructions should identify the workspace path, latest checkpoint, completed/blocked work and next actions so another chat can resume without the original conversation.

If `session.json` itself is missing or invalid, `status` stops with an error. Inspect the numbered checkpoint manifests and their saved sessions directly, verify snapshot hashes, and recover the session to a new location before changing the current workspace. Do not initialize over the existing folder or discard newer package work.
