# Platform discovery and guarded changes

Read before target-specific work. This skill uses available public Arch tools; it contains no default environment, account, endpoint or credential. Discover the installed tool schema each session rather than assuming a fixed toolkit/runtime version.

## Discover only what this slice needs

Use `platform_project_builder` with `action: describe` where available to discover registered domains and authoritative dependencies. On an existing confirmed target, inspect project dependency/readiness information. Read `debug_docs` topic `mcp/project-build-playbook` and relevant feature topics; connected Studio documentation has broader coverage than embedded MCP fallback material. Missing search results in fallback docs are not evidence that a feature is unsupported.

Record documentation source, retrieval date, toolkit/runtime version when available, and whether a capability is documented, configured or actually exercised. Resolve syntax/semantics through current docs and scoped validation, not invented ABL or remembered provider defaults. If access is missing, continue portable/offline work and list exactly which claims need target verification.

The embedded playbook reviewed on 2026-10-09 favors guarded individual-agent edits (`edit_dsl` with the current source hash) and reserves import for whole project packages. These names are discovery leads, not a permanent API guarantee: check the installed schema and follow its current contract.

## Apply the appropriate operation

- For a new project, determine the target and scope before creating it. Reuse an existing target only when identity is confirmed. Read back created IDs and defaults.
- Configure dependencies before references: models, opaque auth profiles/integrations, tools/knowledge/workflows and other required resources. Do not create unrelated features just because the catalog lists them. Secure consent/secret entry uses the platform's secure flow.
- For normal resource edits, use the current guarded edit operation with an exact source version/hash when supported. Whole-project imports are appropriate only for a reviewed package change; preview/validate the complete package and understand replacement/removal semantics first.
- Discover and continue durable operation handles through their registered operations surface when returned. Observe required dependencies and confirmation tokens; do not synthesize platform grants or treat architecture approval as a platform-issued token.
- Read each operation's stated validation/read-back requirements. Inspect a consumed operation with an unknown outcome before retrying; poll its state with backoff rather than starting another operation. A rate-limit or timeout does not justify blind replay.

Compare the live source to the exported baseline before applying. If another actor changed it, reconcile the delta and preserve their work. A local manifest is useful evidence, but is not an atomic concurrency guard.

Version publication, deployment and promotion are distinct from authoring and imports. Perform them only when explicitly authorized and supported by the current contract. A successful import, registered handoff or channel configuration does not prove a real conversation, external transfer or delivered notification.
