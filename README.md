# Kore.ai Codex Plugins

Kore.ai-maintained skills and plugins that help developers, partners, and customers work more effectively with Kore.ai products.

This repository is available under the MIT License, but it is not currently open for external contributions. Kore.ai maintains and publishes the contents of the **Kore Skills** marketplace.

## What you can do with Kore Skills

Each plugin packages one or more focused workflows for Codex. Depending on the installed plugin, you can ask Codex to work with Kore.ai artifacts, guide a design or implementation task, produce structured documentation, or validate an outcome.

Plugins include their own usage guidance, supported inputs, limitations, and example prompts. Some skills may also bundle scripts, reference material, templates, or connections to external tools.

## Available plugins

### Kore XO Tools

Installs `$xo-bot-decomposer`, which analyzes a Kore.ai XO bot-definition JSON, ZIP, or extracted export and produces:

- a business-level inventory of user goals, events, and flow steps;
- a technical reference for integrations, entities, scripts, events, SDK webhooks, helpers and supplied BotKit/configuration evidence; and
- an explicit coverage/dependency register, with coordinated child/shared-runtime analysis for universal systems.

The skill processes supplied files locally, redacts likely credential values from generated evidence, and does not estimate implementation effort. Version `0.4.0` adds selected multi-source intake, recursive node coverage, reviewable dependency gaps and schema-v2 outputs. JavaScript discovery is lexical and requires semantic review; source checks do not establish deployed behavior. See the [input/schema compatibility notes](plugins/kore-xo-tools/skills/xo-bot-decomposer/references/evidence-schema.md).

### Artemis

Installs three skills: `$artemis-designer` creates and reviews governed functional, experience and technical designs; `$artemis-developer` implements or repairs Agent Platform projects; `$artemis-reviewer` reviews built agents against their design through experience and performance specialists. Designer preserves wave scope and traceability; Developer reuses that design and confirms a concise architecture before building one complete use case at a time.

Developer prefers supported native ABL logic and HTTP/API tools, uses Code Tools only for justified exceptions, and balances useful response time with conversational quality. It includes self-contained implementation references, a diagram-based architecture brief, bounded delegation and checkpoint/resume guidance, plus a read-only Python 3.10+ snapshot helper. Live changes and tests use the user's available authorized Arch/platform tools; offline preparation remains possible with evidence gaps disclosed. Deployment and sharing require explicit authorization.

Version `0.7.0` brings the three-skill **Artemis** bundle while preserving the plugin ID `kore-agent-design`. **Artemis Designer** replaces the skill name `kore-agent-designer`; use `$artemis-designer` and update helper paths to `skills/artemis-designer/`. Refresh the installed plugin after release to discover the renamed Designer and new Developer/Reviewer.

All three support plain-language goals and carry context across scoped handoffs. Run each skill's tests using `python3 -m unittest discover -s plugins/kore-agent-design/skills/<skill-name>/tests -v`. Source tests and offline scenarios do not certify installed discovery or a live project/channel.

Reviewer accepts supplied or inferred designs, preserves source snapshots and run history, and coordinates up to two specialist subagents with shared conversation/turn/time limits. It distinguishes actual voice/chat evidence from debug output, links findings to source and traces, and hands authorized repairs to Developer for bounded independent retesting. Defaults of 3 seconds for visible chat response and 2 seconds for audible voice response are configurable review targets. Its read-only Python 3.10+ metrics helper keeps missing/time-out observations and debug measurements distinct. Offline review and sequential fallback remain useful when connections or subagents are unavailable. This public implementation has no dependency on a separate report skill or organization-only services; when duplicate skill names are installed, select Reviewer from the `kore-agent-design` bundle.

### Arch Agent Platform Tools

The `arch-agent-platform` plugin exposes the published [Arch MCP toolkit](https://www.npmjs.com/package/@koreai/arch-mcp-tools) for agent development, evaluation, and diagnostics. It provides MCP tools, not a standalone skill, and can support the optional implementation handoff from Artemis.

Requires Node.js with `npx`, network access to the npm registry, and access to the Agent Platform environment you intend to use. Follow the toolkit's connection guidance using your own authorized account; no credentials or default environment are bundled. Select the target environment explicitly before platform work.

The server launches `npx -y @koreai/arch-mcp-tools@latest`. The toolkit version can therefore change independently of this wrapper; restart the server in a new task to pick up a newly published toolkit. The toolkit has its own licensing and runtime behavior. Installation does not itself authorize project changes or deployment.

## Getting started

### 1. Add the marketplace

From a terminal with Codex installed, add the Kore Skills marketplace directly from GitHub:

```bash
codex plugin marketplace add Koredotcom/kore-skills --ref main
```

### 2. Browse available plugins

```bash
codex plugin list --marketplace kore-skills
```

### 3. Install a plugin

Replace `<plugin-name>` with a plugin listed by the previous command:

```bash
codex plugin add <plugin-name>@kore-skills
```

### 4. Start using it

Start a new Codex task after installation. Describe the outcome you want in plain language and attach any files the workflow needs. Codex can select an applicable skill automatically, or you can explicitly request one by name—for example:

```text
Use $<skill-name> to analyze the attached Kore.ai artifact.
```

Review each plugin's documentation for supported product versions, required inputs, expected outputs, and any setup steps.

### Keep the marketplace current

Refresh the marketplace when Kore.ai publishes updates:

```bash
codex plugin marketplace upgrade kore-skills
```

> [!TIP]
> **Using another coding agent?** The underlying `SKILL.md` instructions are often portable, but plugin marketplaces and integrations are tool-specific. You can clone this repository and ask an agent such as Claude Code or Devin to adapt a selected skill and its supporting files to that agent's native format, then install the adapted copy. Review the changes, scripts, integrations, and requested permissions before enabling it; the Codex marketplace metadata itself will not install unchanged in every agent.

## Repository structure

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json      # Kore Skills marketplace catalog
├── plugins/
│   └── <plugin-name>/
│       ├── .codex-plugin/
│       │   └── plugin.json       # Codex plugin manifest
│       ├── .mcp.json             # Optional MCP server configuration
│       ├── skills/               # Optional skills and their supporting files
│       ├── scripts/              # Optional deterministic helpers
│       ├── references/           # Optional reference material
│       └── assets/               # Optional templates and media
└── README.md
```

## Data and security

- Review a plugin before installing it, especially when it includes scripts or external integrations.
- Do not commit credentials, private keys, customer data, or confidential implementation material to this repository.
- Treat outputs as working material and validate them against the applicable Kore.ai product documentation and your own requirements.
- Do not disclose security vulnerabilities through a public issue. Private reporting instructions will be published before the first general release.

## Maintenance and support

Kore.ai maintains this repository and is not accepting external pull requests at this time. Plugin-specific support information and known limitations will be documented with each published plugin.

These plugins complement, but do not replace, official Kore.ai product documentation and support channels.

### Maintainer safety checks

This repository includes a versioned pre-commit hook and a matching CI check. The checks use Gitleaks to detect known secret formats and a repository-owned scanner to block machine-local paths and sensitive filenames.

After cloning, maintainers should enable the tracked hooks once:

```bash
git config core.hooksPath .githooks
```

The pre-commit hook fails closed when Gitleaks is unavailable. To run the repository-owned check manually across all tracked and unignored files:

```bash
python3 scripts/check_repository_safety.py --all-files
```

Git hooks can be bypassed, so the GitHub Actions workflow repeats both checks for every push and pull request.

## License

Copyright © 2026 Kore.ai, Inc. Released under the [MIT License](LICENSE).

## Project status

The marketplace is being prepared for its first release. Plugin names, interfaces, and installation details may change until a stable catalog is published.
