# General design guidance

Read this reference for every modular package creation or update. It defines rules shared by all document categories.

## Package principles

- Keep Markdown as the canonical editable source. Treat DOCX, PDF, and connected-document versions as derived outputs unless the user explicitly chooses another authority.
- Define each fact in one canonical document and reference it elsewhere by stable identifier and relative link.
- Keep the index authoritative for the document register, wave placement, baseline status, and change history.
- Keep shared agent behavior in the agent definition, functional behavior in the applicable use-case file, modality-specific behavior in the experience file, and implementation decisions in the applicable technical file.
- Preserve supplied terminology and distinguish `Confirmed`, `Documented capability`, `Proposed`, `Assumption`, `TBD`, `Not verifiable`, and `Not applicable`.

## Required metadata

Begin every package document with one category marker and this visible metadata section:

```markdown
<!-- kore-agent-design:<category>:v2 -->
# <Document title>

## Document Metadata

| Field | Value |
|---|---|
| Document ID | DOC-### |
| Document type | <category name> |
| Version | <major.minor> |
| Status | Working Draft \| In Review \| Approved \| Superseded |
| Owner | <name or role> |
| Wave | All \| Wave # \| Proposed \| Not applicable |
| Canonical owner for | <facts and identifiers owned here> |
| Source evidence | <artifact links, document names, or conversations> |
| Last updated | <YYYY-MM-DD> |
```

Use one of these marker categories: `index`, `agent-definition`, `use-case`, `voice-experience`, `digital-experience`, `architecture`, `connectivity-integrations`, `use-case-apis`, `data-security`, `operations-testing-release`, or `review`.

The document register in `00-design-index.md` must match each document's ID, relative path, type, version, status, and wave.

## Identifier registry

Use three digits and never recycle an identifier:

| Prefix | Meaning | Canonical owner |
|---|---|---|
| `DOC-###` | Package document | Index and document metadata |
| `FND-###` | Foundation item | Index |
| `UC-###` | User goal or process use case | Use-case document |
| `FR-###` | Functional requirement | Use-case or agent-definition document |
| `BR-###` | Business rule | Use-case or agent-definition document |
| `EXP-###` | Experience requirement | Experience document |
| `NFR-###` | Non-functional requirement | Agent definition or technical document |
| `INT-###` | Integration requirement | Connectivity and integrations document |
| `API-###` | API operation or contract | Use-case APIs document |
| `AC-###` | Acceptance criterion | Use-case or experience document |
| `TD-###` | Technical decision | Applicable technical document |
| `OQ-###` | Open question | Index or canonical category document |
| `CHG-###` | Controlled design change | Index |

Define an identifier once. References may repeat it. When retiring an item, retain the identifier and mark it `Superseded`, `Deferred`, or `Removed` with rationale and effective version. Never renumber to close gaps.

## Links and traceability

- Use relative Markdown links for package files and local diagrams.
- Link a referenced identifier to its canonical file when practical.
- Every Wave 1 use case must trace to acceptance criteria and technical treatment.
- Every integration, API, component, model, prompt, tool, knowledge source, and guardrail must trace to a functional or non-functional need.
- Keep secrets and secure values out of the package; use opaque credential or authorization-profile references.

## Change control

Before changing an approved fact, identify inbound and outbound references and record a `CHG-###` entry in the index with rationale, affected IDs and documents, owner, approval state, and effective version. Preserve the previous baseline in history.

A change to shared behavior may affect every use case. A change to a use case may affect experience, integrations, APIs, data, security, tests, release scope, and wave feasibility. Reconcile all affected documents before approving the change.

## Document evolution

- Treat the marker version as the package schema version. Do not silently mix different modular schema versions in one package.
- Review legacy v1 functional and technical files in place. When migration is requested, create a v2 package in the approved working folder, register the legacy files as source evidence, preserve existing identifiers where their meaning is unchanged, and record material remapping decisions.
- Increment a document's minor version for approved clarifications or compatible additions. Use a major version when its scope, ownership, or approved behavior changes materially.
- Retain retired requirements and decisions with `Superseded`, `Deferred`, or `Removed` status, rationale, replacement identifier when applicable, and effective version.
- Moving an item between waves requires a `CHG-###`, impact review, updated approval state, and reconciliation of every affected document. The prior baseline remains visible in change history.
- Regenerate derived outputs after canonical Markdown changes and label them with the canonical package version.

## Writing standard

- State observed facts separately from recommendations and unresolved choices.
- Use measurable thresholds for requirements where evidence supports them.
- Use `Not applicable — <reason>` instead of deleting a required consideration.
- Do not copy the same requirement into several files. Summarize and link.
- Prefer Mermaid for diagrams that remain readable as text; keep external diagrams linked and named in the evidence register.
- Do not leave raw template prompts in delivered documents.
