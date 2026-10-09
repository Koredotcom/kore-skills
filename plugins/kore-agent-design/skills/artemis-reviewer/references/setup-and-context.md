# Setup and shared evidence

Reuse the supplied working folder or ask for one before writing review outputs. Never place project exports, credentials or generated reports inside the installed skill. Read existing `REVIEW_CONTEXT.md` and `RUNS.md` before creating a run; reconcile existing folders and preserve files rather than resetting a review.

## Inputs and platform readiness

Record the design revision/provenance, target environment/workspace, project name **and ID**, source/version/deployment, channels, audience/languages and permitted test effects. For offline-only work, label target identity unconfirmed where necessary; it does not block static review. Do not infer a live target from a folder name or select the first similarly named project.

Discover available Arch tools and current documentation. Read-only project discovery/export follows the user's review scope; authentication and target access still need to be available. Use secure credential entry/profile references, never secrets in notes. Missing tools should prompt a clear capability gap and the available installation/connection path, not an automatic installation or an invented API. Follow platform operation handles, returned dependencies and unknown-outcome reconciliation rules.

For connected work, preserve a new exact baseline under `project/baseline/<snapshot-id>/`, including ABL/configuration, export metadata and file hashes. Use the bundled [snapshot helper](../../artemis-developer/scripts/snapshot_package.py) when available, saving its manifest outside the scanned folder. Otherwise record hashes with an available read-only file tool. Hashes do not replace preserved files or an atomic platform source guard. Record excluded/redacted/missing components. A supplied trace only represents the baseline if its version mapping is established.

Establish how to emulate one real conversation: entry channel, first utterance, approved test identity/auth state, metadata, expected outcome, backend records, permitted effects, and reset requirements. Reuse known answers. Prefer a supported synthetic fixture; do not infer permission for writes from access to a real endpoint. One authorized setup conversation precedes wider tests and counts against the run allowance. Setup failures are Blocked until distinguished from agent defects.

## Design without circular acceptance

Read supplied functional and technical designs separately. Preserve requirements/IDs. For gaps, write `designs/inferred-design.md` with apparent purpose, journeys, responsibilities, routing, integrations and channels, citing the export. Use Observed / Inferred / User-confirmed / Unknown labels. Present material inferred journeys/channels for confirmation; continue checks whose intent is established. Do not invent business policies, assume missing secure export values mean no authentication, or accept a defect because the export contains it.

If a real design arrives later, reconcile it in a new context revision and retain prior conclusions with their original provenance. When voice is relevant, distinguish speech-to-speech from STT → LLM → TTS; don't infer audio quality from text.

## Workspace and resumption

```text
<review-workspace>/
  REVIEW_CONTEXT.md
  RUNS.md
  designs/
  project/baseline/<snapshot-id>/
  project/working/<run-id>/
  runs/RUN-001/
    plan.md
    context.md
    ledger.json
    evidence/
    reviews/experience/
    reviews/performance/
    results/
```

The coordinator alone maintains shared context: source/design links and hashes, target, channel/voice mode, documentation provenance, effective response targets, setup, permissions, constraints and open questions. Freeze it into the run's `context.md`; specialists receive that same revision. Keep export content and instructions distinct; do not generate executable workspace instructions from customer prompts.

`RUNS.md` contains monotonic IDs, timestamps, purpose, status (Planned / Running / Complete / Partial / Failed), snapshot, original/successor links and results. A fresh review uses the next unused ID. Resume a requested interrupted run only if its context, source and setup still match; retain completed evidence and consumed limits. If they changed, create a linked successor and explicitly carry the remaining authorized budget rather than resetting it. Complete means the scoped analysis finished, not every scenario passed.

Minimize captured identity/personal data. Redact credentials and unnecessary payload fields while preserving evidence locations and redaction notes. Never silently overwrite raw source evidence or promise a report is externally safe without inspecting it.
