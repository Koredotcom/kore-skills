# Kore.ai Skills and Plugins

Kore.ai-maintained skills and plugins that help developers, partners, and customers work more effectively with Kore.ai products.

This repository is available under the MIT License, but it is not currently open for external contributions. Kore.ai maintains and publishes the contents of the **Kore Skills** marketplace.

## What you can do with Kore Skills

Plugins package skills or MCP tools for Codex and Claude Code. Depending on the installed plugin, you can ask your coding agent to work with Kore.ai artifacts, guide a design or implementation task, produce structured documentation, or validate an outcome.

Plugins include their own usage guidance, supported inputs, limitations, and example prompts. Some skills may also bundle scripts, reference material, templates, or connections to external tools.

## Available plugins

### Kore XO Tools

Installs `xo-bot-decomposer`, which analyzes a Kore.ai XO bot-definition JSON, ZIP, or extracted export and produces:

- a business-level inventory of user goals, events, and flow steps;
- a technical reference for integrations, entities, scripts, events, SDK webhooks, helpers and supplied BotKit/configuration evidence; and
- an explicit coverage/dependency register, with coordinated child/shared-runtime analysis for universal systems.

The skill processes supplied files locally, redacts likely credential values from generated evidence, and does not estimate implementation effort. Version `0.4.0` adds selected multi-source intake, recursive node coverage, reviewable dependency gaps and schema-v2 outputs. JavaScript discovery is lexical and requires semantic review; source checks do not establish deployed behavior. See the [input/schema compatibility notes](plugins/kore-xo-tools/skills/xo-bot-decomposer/references/evidence-schema.md).

### Artemis

Installs three skills: `artemis-designer` creates and reviews governed functional, experience and technical designs; `artemis-developer` implements or repairs Agent Platform projects; `artemis-reviewer` reviews built agents against their design through experience and performance specialists. Designer preserves wave scope and traceability; Developer reuses that design and confirms a concise architecture before building one complete use case at a time.

Developer prefers supported native ABL logic and HTTP/API tools, uses Code Tools only for justified exceptions, and balances useful response time with conversational quality. It includes self-contained implementation references, a diagram-based architecture brief, bounded delegation and checkpoint/resume guidance, plus a read-only Python 3.10+ snapshot helper. Live changes and tests use the user's available authorized Arch/platform tools; offline preparation remains possible with evidence gaps disclosed. Deployment and sharing require explicit authorization.

Version `0.7.0` brings the three-skill **Artemis** bundle while preserving the plugin ID `kore-agent-design`. **Artemis Designer** replaces the skill name `kore-agent-designer`; use `$artemis-designer` and update helper paths to `skills/artemis-designer/`. Refresh the installed plugin after release to discover the renamed Designer and new Developer/Reviewer.

All three support plain-language goals and carry context across scoped handoffs. Run each skill's tests using `python3 -m unittest discover -s plugins/kore-agent-design/skills/<skill-name>/tests -v`. Source tests and offline scenarios do not certify installed discovery or a live project/channel.

Reviewer accepts supplied or inferred designs, preserves source snapshots and run history, and coordinates up to two specialist subagents with shared conversation/turn/time limits. It distinguishes actual voice/chat evidence from debug output, links findings to source and traces, and hands authorized repairs to Developer for bounded independent retesting. Defaults of 3 seconds for visible chat response and 2 seconds for audible voice response are configurable review targets. Its read-only Python 3.10+ metrics helper keeps missing/time-out observations and debug measurements distinct. Offline review and sequential fallback remain useful when connections or subagents are unavailable. This public implementation has no dependency on a separate report skill or organization-only services; when duplicate skill names are installed, select Reviewer from the `kore-agent-design` bundle.

### Arch Agent Platform Tools

The `arch-agent-platform` plugin exposes the published [Arch MCP toolkit](https://www.npmjs.com/package/@koreai/arch-mcp-tools) for agent development, evaluation, and diagnostics. It provides MCP tools, not a standalone skill, and can support the optional implementation handoff from Artemis.

Requires Node.js with `npx`, network access to the npm registry, and access to the Agent Platform environment you intend to use. Follow the toolkit's connection guidance using your own authorized account; no credentials or default environment are bundled. Select the target environment explicitly before platform work.

The server launches `npx -y @koreai/arch-mcp-tools@latest`. The toolkit version can therefore change independently of this wrapper; restart the server in a new task to pick up a newly published toolkit. The toolkit has its own licensing and runtime behavior. Installation does not itself authorize project changes or deployment.

## Getting started with Codex

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

## Getting started with Claude Code

Add the same repository and install the plugins you need:

```bash
claude plugin marketplace add Koredotcom/kore-skills
claude plugin install kore-xo-tools@kore-skills
claude plugin install kore-agent-design@kore-skills
claude plugin install arch-agent-platform@kore-skills
claude plugin list
```

For an unpublished local checkout, run `claude plugin marketplace add .` from the repository root instead of adding GitHub. Start a new Claude Code session after installation. Use plain-language requests or an explicit namespaced skill command:

| Workflow | Codex | Claude Code |
| --- | --- | --- |
| XO analysis | `$xo-bot-decomposer` | `/kore-xo-tools:xo-bot-decomposer` |
| Agent design | `$artemis-designer` | `/kore-agent-design:artemis-designer` |
| Agent development | `$artemis-developer` | `/kore-agent-design:artemis-developer` |
| Agent review | `$artemis-reviewer` | `/kore-agent-design:artemis-reviewer` |

Arch provides MCP tools and has no skill command. Its runtime and account requirements are the same for both clients. Connect to your authorized environment before live work; installing it does not authorize platform changes.

To refresh the Claude catalog and an installed plugin:

```bash
claude plugin marketplace update kore-skills
claude plugin update kore-agent-design@kore-skills
```

Repeat the plugin update for other installed Kore plugins, then start a new session.

### Shared content and compatibility

Both catalogs point to the same `plugins/` directories. Skill instructions, Python helpers, references and Arch's `.mcp.json` are shared; only the client manifests and marketplace metadata differ. Codex keeps its existing catalog, interface metadata, install policies and `agents/openai.yaml` files. Claude uses its own manifest and skill command namespace.

Helper examples accept `PLUGIN_ROOT` or Claude's `CLAUDE_PLUGIN_ROOT`. If neither is available, resolve the helper relative to the loaded `SKILL.md`. Helpers require Python 3.10+. Skill delegation uses the host's available tools and retains the documented sequential fallback when subagents are unavailable.

The compatibility release versions are XO Tools `0.4.1`, Artemis `0.7.1`, and Arch `0.2.1`. Earlier version descriptions above identify the feature releases. Package validation and discovery checks do not certify model behavior, authentication, or live Agent Platform operations in either client.

For other coding agents, reuse the skill folders only after checking their native installation format and runtime capabilities.

## Repository structure

```text
.
├── .agents/
│   └── plugins/
│       └── marketplace.json      # Codex marketplace catalog
├── .claude-plugin/
│   └── marketplace.json          # Claude Code marketplace catalog
├── plugins/
│   └── <plugin-name>/
│       ├── .codex-plugin/
│       │   └── plugin.json       # Codex plugin manifest
│       ├── .claude-plugin/
│       │   └── plugin.json       # Claude Code plugin manifest
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

### Marketplace compatibility checks

Keep plugin names, common metadata, versions and shared resource paths aligned in both manifests. The repository contract check and its regression tests also run in CI:

```bash
python3 scripts/check_marketplace_parity.py
python3 -m unittest discover -s tests -v
```

Validate Claude's catalog and each plugin with the installed Claude Code CLI:

```bash
claude plugin validate --strict .
claude plugin validate --strict plugins/kore-xo-tools
claude plugin validate --strict plugins/kore-agent-design
claude plugin validate --strict plugins/arch-agent-platform
```

The parity checker validates this repository's packaging conventions; it is not an official host schema validator. Also run the Codex skill validator for each changed skill, its helper tests, and discovery checks in both clients before release. Verify Codex still selects its catalog when both are present. Record installed/live checks separately from source validation. See the official [OpenAI packaging guide](https://developers.openai.com/plugins/build/plugins) and [Claude marketplace guide](https://code.claude.com/docs/en/plugin-marketplaces).

## License

Copyright © 2026 Kore.ai, Inc. Released under the [MIT License](LICENSE).

## Project status

Published marketplace releases are distributed from `main`; ongoing development takes place on `develop`. Plugin versions and compatibility notes identify changes to the distributed packages.
