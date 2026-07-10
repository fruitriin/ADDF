<p align="center">
  <img src=".claude/assets/gh-readme-light.png" alt="ADDF — Agentic Driven Development Framework" width="640">
</p>

# AutomatonDevDrive Framework

> ADDF — Agentic Driven Development Framework

[![test](https://github.com/fruitriin/ADDF/actions/workflows/test.yml/badge.svg)](https://github.com/fruitriin/ADDF/actions/workflows/test.yml)

[日本語版 README はこちら](README.md)

A repository scaffolding framework for AI coding agents.
Install ADDF into your project and it provides plan-driven development, knowhow accumulation, and quality gates — AI agents autonomously select tasks, implement them, and run quality verification end to end.

**ADDF is a repository scaffolding framework — it contains no application framework.** It works with any tech stack: React, Rails, Flutter, Unity, and beyond.

## Supported Agents

| Agent | Support | Notes |
|---|---|---|
| **Claude Code** (Anthropic) | First-party | Full feature support. Hooks, Skills, Agents, parallel execution |
| **Codex** (OpenAI) | Partial | Plan-driven workflow & knowhow work. Hooks & auto quality gates limited → [Details](.claude/addf/guides/codex-setup.md) |
| **Others** (Open Code, etc.) | Basic | Plan-driven workflow works if the agent reads CLAUDE.md / AGENTS.md |

## Features

- **Plan-Driven** — Review plans, not code. AI ensures implementation quality
- **Knowhow Accumulation** — Records implementation insights in `.claude/addf/knowhow/` and auto-references them
- **Self-Driving** — `/addf-dev` completes one task; `/loop 1h /addf-dev` for continuous execution
- **Quality Gate** — Automatically runs code review, security review, and contribution detection
- **Separation of Skills and Experience** — Skill definitions (`.md`) and experience (`.exp.md`) are separated

## Quick Start

### 1. Install ADDF

**New project** — from GitHub Template:

```bash
# Use this template → create repo → clone
git clone https://github.com/your-org/my-project.git
cd my-project
```
```
/addf-init
```

**Existing project** — run this in Claude Code:

```
Fetch https://raw.githubusercontent.com/fruitriin/ADDF/main/.claude/commands/addf-init.md
and install the ADDF framework into this project.
ADDF repository: https://github.com/fruitriin/ADDF
```

Existing CLAUDE.md, AGENTS.md, and config files are automatically migrated and merged.

### 2. Create Plans and Start Development

```markdown
- Add login feature
- Increase test coverage
```

Just hand it to Claude and the AI will break it into plan files in `.claude/addf/plans/` and `TODO.md`.

```
/addf-dev
```

Picks one task, implements it, runs quality verification, and commits. For continuous execution:

```
/loop 1h /addf-dev
```

## Skills

Skills provided by ADDF (invoked via `/command-name`):

| Skill | Invocation | Description |
|---|---|---|
| **addf-dev** | `/addf-dev` | Picks a task from TODO, implements, verifies quality, and commits |
| **addf-init** | `/addf-init [check]` | Project initialization / structure verification |
| **addf-release** | `/addf-release [minor]` | Release (changelog, version bump, publish) |
| **addf-migrate** | `/addf-migrate` | Upgrade ADDF framework to latest version |
| **addf-knowhow** | `/addf-knowhow <topic>` | Record implementation insights (with dedup & merge) |
| **addf-knowhow-index** | `/addf-knowhow-index [reindex]` | View or rebuild the knowhow index |
| **addf-lint** | `/addf-lint` | Framework integrity check |
| **addf-permission-audit** | `/addf-permission-audit` | Analyze and classify permission requests |
| **addf-mode** | `/addf-mode [unattended]` | View or switch the 3-axis "when in doubt" doctrine modes |
| **addf-speculate** | `/addf-speculate [clean]` | Idle-time speculative development in worktrees (opt-in; never auto-merged to mainline) |

<details>
<summary>Other skills</summary>

| Skill | Description |
|---|---|
| **addf-knowhow-filter** | Filter knowhow relevant to a Plan |
| **addf-knowhow-revise** | Re-verify and correct stale knowhow |
| **addf-knowhow-network** | Cross-link knowhow articles into a wiki |
| **addf-overview** | Generate ecosystem overview docs in `.claude/addf/project-overview/` |
| **addf-experience** | Validate experience file (`.exp.md`) reference self-consistency and format health |
| **addf-gui-test** | Run GUI tests (macOS optional) |
| **addf-annotate-grid** | Draw grid lines on PNG images |
| **addf-clip-image** | Clip regions from PNG images |

</details>

## Built-in Agents

Sub-agents auto-launched during quality gates. Customize or add agents to fit your project.

| Agent | Purpose | Customization guidance |
|---|---|---|
| **addf-knowhow-agent** | Filters knowhow relevant to a Plan | — |
| **addf-code-review-agent** | Reviews code quality and readability | Add your project's coding conventions |
| **addf-security-review-agent** | Inspects security vulnerabilities (optional) | Add industry-specific security standards |
| **addf-contribution-agent** | Detects framework contribution candidates | — |
| **addf-ui-test-agent** | Screenshot-based UI verification (optional) | **Rewrite as your project's UI/UX domain expert** |

> **Tester agents should be domain experts for your project.**
> Customize agent definitions in `.claude/agents/` with your project's domain knowledge, test criteria, and quality requirements.
> Example: For an e-commerce site, add payment flow verification steps. For iOS Native, add automated testing via iOS Simulator.

## Documentation

| Guide | Content |
|---|---|
| [Detailed Setup](.claude/addf/guides/setup.md) | Manual setup, configuration roles, directory structure |
| [Built-in Agents](.claude/addf/guides/agents.md) | Sub-agents for quality gates and how to customize them |
| [Development Process](.claude/addf/guides/development-process.md) | Boot sequence, quality gates, task lifecycle |
| [Migration](.claude/addf/guides/migration.md) | Upgrading ADDF with `/addf-migrate` |
| [Speculative Development](.claude/addf/guides/speculative-development.md) | Overview of idle-time worktree speculation (two-layer model, promotion, cleanup) |
| [PR Format](.claude/addf/guides/pr-format.md) | Standard PR body format (plan links, progress position) |
| [Codex Setup](.claude/addf/guides/codex-setup.md) | Using ADDF with OpenAI Codex CLI |
| [GUI Testing](.claude/addf/guides/gui-test-setup.md) | macOS GUI test setup |

## About the Name

The official name of this framework is **AutomatonDevDrive Framework**.

But if you take its initials — **ADDF** — and expand them, you get: **A**gentic **D**riven **D**evelopment **F**ramework.

Not a coincidence.

An Automaton is exactly what the AI agent is: something that autonomously selects tasks, implements them, and verifies quality — no hand-holding required. DevDrive is the engine that keeps it moving, the mechanism that propels development forward.

The surface name is Automaton. The hidden name is Agentic. Both describe the same thing.
If you caught that — nice.
