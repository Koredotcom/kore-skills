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

The skill processes supplied files locally, redacts likely credential values from generated evidence, and does not estimate implementation effort. Version `0.4.0` adds selected multi-source intake, recursive node coverage, reviewable dependency gaps and schema-v2 outputs. Version `0.5.0` recognizes universal-bot configuration, discovers linked exports within supplied inputs, and resolves parent/linked welcome and fallback task ownership using exported IDs. A user-selected name mode supports source discovery when registry IDs are defective; ambiguous ID-only routes remain unresolved. The skill requests missing child/BotKit sources and coordinates parent/shared analysis, child passes and end-to-end reconciliation. JavaScript discovery is lexical and requires semantic review; source checks do not establish deployed behavior. See the [input/schema compatibility notes](plugins/kore-xo-tools/skills/xo-bot-decomposer/references/evidence-schema.md).

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

## Choose an installation method

| Setup | Use this guide |
| --- | --- |
| Install native plugins for Codex | [Codex setup](#getting-started-with-codex) |
| Install native plugins for Claude Code | [Claude Code setup](#getting-started-with-claude-code) |
| Share a repeatable project setup across Claude Code and Codex | [Microsoft APM setup](#getting-started-with-microsoft-apm) |

Use one installation method per capability in a project to avoid duplicate skills or MCP registrations. Install and sign in to your chosen client first. Python 3.10+ is required for bundled skill helpers; Arch additionally requires Node.js with `npx` and access to your Agent Platform environment. The terminal instructions below target Codex and Claude Code; they do not configure Claude Desktop's separate plugin interface.

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

### 3. Install the plugins you need

```bash
codex plugin add kore-agent-design@kore-skills
codex plugin add kore-xo-tools@kore-skills
codex plugin add arch-agent-platform@kore-skills
```

`kore-agent-design` installs the complete Artemis Designer, Developer and Reviewer bundle. Skip any package you do not need.

### 4. Start using it

Start a new Codex task after installation. Describe the outcome you want in plain language and attach any files the workflow needs. Codex can select an applicable skill automatically, or you can explicitly request one by name—for example:

```text
Use $artemis-designer to help design an agent from the attached requirements.
```

Review each plugin's documentation for supported product versions, required inputs, expected outputs, and any setup steps.

### Keep the marketplace current

Refresh the marketplace when Kore.ai publishes updates:

```bash
codex plugin marketplace upgrade kore-skills
```

## Getting started with Claude Code

The **Artemis** plugin bundles **Artemis Designer**, **Artemis Developer** and **Artemis Reviewer**. Its Claude marketplace entry and manifest declare `displayName: "Artemis"`; the stable package ID and command namespace remain `kore-agent-design`.

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

## Getting started with Microsoft APM

[Microsoft Agent Package Manager (APM)](https://microsoft.github.io/apm/) installs this repository's existing Claude marketplace packages into your project for Claude Code and Codex. It reuses the same skills, helpers and MCP definition; no separate skill copies are needed.

### 1. Install APM

Install Git and follow the [official APM installation guide](https://microsoft.github.io/apm/getting-started/installation/) for your operating system. For example, on macOS or Linux with Homebrew:

```bash
brew install apm
apm --version
```

This repository's setup was validated with APM `0.33.0`. The skill-helper and Arch prerequisites listed above still apply.

### 2. Admin or project maintainer: choose the packages once

Open a terminal in **your own project or shared project template**, then run:

```bash
apm marketplace add Koredotcom/kore-skills
apm install kore-agent-design@kore-skills kore-xo-tools@kore-skills arch-agent-platform@kore-skills --target claude,codex
```

Select only the packages you need. Use `--target claude` or `--target codex` for a single client. The packages are:

| Package | Included capabilities |
| --- | --- |
| `kore-agent-design` | Artemis Designer, Developer and Reviewer—all three install together |
| `kore-xo-tools` | XO Bot Decomposer |
| `arch-agent-platform` | Arch MCP tools for authorized platform work |

`Koredotcom/kore-skills` is GitHub `owner/repository` shorthand. The full URL `https://github.com/Koredotcom/kore-skills` also works with `apm marketplace add`. In `kore-agent-design@kore-skills`, APM resolves the package before `@` from the registered marketplace after `@`.

APM creates `apm.yml` with the selected targets and resolved repository package paths, plus `apm.lock.yaml` recording the installed revisions. Review and commit these files and the generated target configuration/skill files in your consumer project; keep `apm_modules/` ignored. Review generated metadata and configuration for local identity or credentials before sharing. See [APM's install and source-control guidance](https://microsoft.github.io/apm/consumer/install-packages/).

### 3. Team members: restore the shared setup

After installing APM and cloning the configured project or creating a project from its template, run from that project's root:

```bash
apm install
```

Team members do **not** need to name each skill or repeat marketplace registration: the committed manifest already identifies the packages and targets. For CI or a strict lockfile restore, use `apm install --frozen`. Keep the restored `apm_modules/` directory available because installed skills can link to its supporting content.

The marketplace is a shared catalog. Registering or installing it on an admin's computer does not install it on everyone else's computer. Use a shared project/template for this onboarding flow; use your organization's provisioning tooling if installation must run automatically. Administrators can additionally govern allowed sources and packages through [APM organization policy](https://microsoft.github.io/apm/enterprise/policy-reference/).

### 4. Use and update the skills

Open Claude Code or Codex in the configured project and start a new session. Ask for the skill by name, for example:

```text
Use Artemis Designer to turn these requirements into a reviewed agent design.
Use Artemis Developer to implement the approved design.
Use Artemis Reviewer to review this agent against its design.
```

APM deploys standalone skills into `.claude/skills/` and `.agents/skills/`; the native Claude plugin namespace in the earlier table does not apply to this installation method. Arch's MCP configuration is written to `.mcp.json` and `.codex/config.toml`. Complete any client trust/connection prompts and connect your own authorized Agent Platform account before live work. Installation alone does not authenticate or authorize platform changes.

For helper commands, resolve `scripts/` relative to the installed skill's `SKILL.md` when plugin-root environment variables are unavailable. Designer supports packages located under hidden directories such as `.agents/` and `.claude/` starting with Artemis `0.7.3`.

The project maintainer can check and apply package updates with:

```bash
apm outdated
apm update
```

Review and validate the changed lockfile and generated files before committing them. Teammates then pull the project changes and run `apm install` again. For a fixed approved release, pin dependencies to a Git commit or tag; see [APM dependency management](https://microsoft.github.io/apm/consumer/manage-dependencies/).

Validation covered all three packages, all four skills and their resources, plus Arch's generated configuration for both clients. It did not include model-driven handoffs, Claude Desktop installation or live Agent Platform authentication and operations.

## Shared content and compatibility

Both catalogs point to the same `plugins/` directories. Skill instructions, Python helpers, references and Arch's `.mcp.json` are shared; only the client manifests and marketplace metadata differ. Codex keeps its existing catalog, interface metadata, install policies and `agents/openai.yaml` files. Claude uses its own manifest and skill command namespace.

Helper examples accept `PLUGIN_ROOT` or Claude's `CLAUDE_PLUGIN_ROOT`. If neither is available, resolve the helper relative to the loaded `SKILL.md`. Helpers require Python 3.10+. Skill delegation uses the host's available tools and retains the documented sequential fallback when subagents are unavailable.

The package versions in this source are XO Tools `0.5.0`, Artemis `0.7.3`, and Arch `0.2.1`. Artemis `0.7.2` adds the Claude display name; `0.7.3` fixes Designer package scanning when the package itself or an ancestor directory is hidden, while still excluding hidden files and folders inside the package. Earlier version descriptions above identify the feature releases. Package validation and discovery checks do not certify model behavior, authentication, or live Agent Platform operations in either client.

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
