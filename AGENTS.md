# Public Repository Guidance

## Purpose and Scope

This is the public, Kore.ai-maintained marketplace for reusable skills and plugins that help people work with Kore products. The repository is publicly available for use, but Kore.ai is not currently accepting external contributions.

Keep this repository separate from internal FDE, delivery, sales engineering, or employee-only skill repositories. Material copied from an internal source must be reviewed and rewritten for public use before it enters this repository.

## Public-Content Boundary

- Never add customer or engagement data, credentials, API keys, tokens, private endpoints, employee-only documentation, internal process details, private repository links, or personal contact information.
- Use synthetic, anonymized fixtures and public product documentation. Redaction is not a substitute for checking whether an artifact is suitable for publication.
- Do not copy an internal skill verbatim. Remove internal terminology, private workflows, employee role assumptions, and dependencies unavailable to public users.
- Do not commit machine-specific paths or local configuration. Use repository-relative paths or `${PLUGIN_ROOT}` for bundled plugin resources.
- Put maintainer-facing contact information behind a public team alias rather than an individual's address.

## Repository and Marketplace Structure

- The Codex marketplace catalog is `.agents/plugins/marketplace.json`; the Claude Code catalog is `.claude-plugin/marketplace.json`. Both use the stable marketplace name `kore-skills`; Codex displays `Kore Skills`.
- Keep each canonical plugin under `plugins/<plugin-name>/` with separate `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` manifests pointing to the same skills and resources. Preserve Codex interface and policy metadata in the Codex files.
- Keep shared manifest metadata and versions aligned across both clients. Run `python3 scripts/check_marketplace_parity.py` to detect drift; do not duplicate skill implementations for a client.
- Put skill instructions under `skills/<skill-name>/SKILL.md`, discovery metadata under `agents/openai.yaml`, and executable helpers under `scripts/`.
- Keep plugin directory names, manifest names, marketplace entries, and documentation aligned.
- Append new marketplace entries unless a deliberate reordering is part of the change.
- Increment the plugin version whenever distributed plugin content changes.

## Public Skill Authoring

- Write for people using Kore products, not for Kore employees delivering an internal process.
- Explain the user outcome, required inputs, produced outputs, limitations, and any supported product-version differences.
- Preserve meaningful Kore product terminology and clarify version-dependent mappings rather than silently normalizing them.
- Separate facts observed in supplied artifacts from inferred intent, especially when exports may omit environment-specific or secured values.
- Use deterministic helpers for repeated parsing, validation, and transformation. Keep semantic judgment in the skill instructions rather than hiding it in brittle automation.
- Keep dependencies minimal, portable, and documented. Do not assume access to internal MCP servers, templates, drives, systems, or credentials.
- Use synthetic fixtures that cover materially different supported cases. Never use raw customer exports as examples or tests.
- Keep shared skill workflows portable across Codex and Claude Code. Document client-specific invocation and plugin-root resolution explicitly; preserve `agents/openai.yaml` for Codex discovery. Do not assume identical tool names or subagent availability across clients.

## Validation and Repository Safety

- Run skill and plugin validators applicable to every changed package.
- Test executable helpers against representative synthetic fixtures and verify deterministic outputs are stable.
- Run `python3 scripts/check_repository_safety.py --all-files` and the repository's Gitleaks check before proposing a commit.
- Do not bypass `.githooks/pre-commit`. If a hook cannot run, reproduce its checks manually and explain why.
- Inspect `git status`, the exact staged file list, and the staged diff before committing. Stage only files intended for the current change.
- Never commit generated output unless it is an intentional distributable asset, example, or fixture.
- Do not push changes without explicit maintainer approval after review.

## Review Priorities

Treat the following as release blockers:

- credentials, tokens, private endpoints, local filesystem paths, or customer/internal material;
- an undocumented dependency on employee-only tools or data;
- inconsistencies between a plugin directory, manifest, marketplace entry, and README;
- unsafe handling of Kore exports or authentication configuration;
- unsupported product-version claims presented as facts;
- missing validation evidence for behavior changed by the proposal; or
- a distributed plugin change without an appropriate version increment.

Local personal instructions belong in ignored files such as `AGENTS.local.md` or `AGENTS.override.md`; local agent state belongs outside this repository. `CLAUDE.md` and its local variants remain ignored local instructions; distributable Claude metadata belongs in `.claude-plugin/`. Shared public guidance belongs in this file.
