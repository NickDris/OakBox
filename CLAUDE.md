# OakBox — AI-Assisted Web Development Scaffolding

## Project Overview

OakBox is a multi-agent AI development pipeline with a Python orchestrator that
drives six specialized agents in sequence. Each agent is invoked via the Claude
API with tool-use capability (read/write files, run commands). State is stored
in machine-readable YAML files so the pipeline is fully resumable.

**Tech stack:** Python 3.12, React (TypeScript), Docker, PostgreSQL

---

## Quick Start

```bash
# 1. Install pipeline dependencies
uv sync

# 2. Set your API key
export ANTHROPIC_API_KEY=sk-...

# 3. Create a new feature
make feature-new ID=001 TITLE="Add user auth" DESC="JWT-based login and registration"

# 4. Run the full pipeline
make feature-run ID=001

# 5. Check status at any time
make feature-status ID=001

# 6. Resume from a specific phase (e.g. after fixing a blocker)
make feature-run-from ID=001 FROM=coder
```

---

## Agent Pipeline

Six agents run in strict order. Each agent uses the Claude API in a tool-use
loop — it can read files, write files, and run allowed commands before signalling
completion with a structured YAML output.

| # | Agent | Role | System prompt |
|---|-------|------|---------------|
| 1 | **Architect** | Designs system-level approach, APIs, data models, file plan | `.oakbox/agents/architect.md` |
| 2 | **Planner** | Decomposes the design into atomic, ordered tasks with acceptance criteria | `.oakbox/agents/planner.md` |
| 3 | **Coder** | Implements each task, runs lint/typecheck | `.oakbox/agents/coder.md` |
| 4 | **Tester** | Writes and runs tests for every acceptance criterion | `.oakbox/agents/tester.md` |
| 5 | **Memory** | Persists decisions, patterns, and gotchas to memory files | `.oakbox/agents/memory.md` |
| 6 | **Docs** | Writes developer and user documentation | `.oakbox/agents/docs.md` |

### Feedback loop

If the Tester phase fails, the orchestrator automatically resets Coder and
Tester to `pending` and re-runs them. Maximum 3 re-entry cycles before the
feature is marked `blocked`.

Memory and Docs **always** run after a successful Tester pass, regardless of
how many Coder re-entries occurred.

---

## How the Orchestrator Works

### `oakbox/` Python package

| Module | Purpose |
|--------|---------|
| `state.py` | Load/save YAML state; manage phase transitions |
| `tools.py` | Tool schemas (read_file, write_file, run_command, etc.) + execution |
| `context.py` | Assemble system prompt + user message per phase |
| `agents.py` | Claude API tool-use loop; returns `complete()` output |
| `pipeline.py` | Drive the phase sequence; handle tester verdict + re-entry; flush memory |
| `cli.py` | `oakbox new / run / status / list` CLI commands |

### State file (YAML)

Each feature has one file in `.oakbox/status/FEAT-<id>-<slug>.yaml`. It is the
single source of truth. The orchestrator reads and writes it — never edit it
manually during a run.

```yaml
id: "001"
title: "Add user auth"
description: "..."
phases:
  architect:
    status: done          # pending | in_progress | done | blocked
    started_at: "..."
    completed_at: "..."
    output: { ... }       # structured output from the agent
  coder:
    status: pending
    re_entry_count: 0     # incremented on each Tester->Coder re-entry
    ...
```

### Agent tools

| Tool | Who can use it | What it does |
|------|---------------|--------------|
| `read_file` | all | Read any file in the repo |
| `list_directory` | all | List directory contents |
| `search_files` | all | Grep across files |
| `write_file` | coder, tester, memory, docs | Write/overwrite a file |
| `run_command` | coder, tester | Run lint/test/typecheck (allowlisted prefixes only) |
| `complete` | all | Signal done + return structured output |

---

## Directory Layout

```
OakBox/
  CLAUDE.md                         # This file — master reference
  Makefile                          # DevOps + pipeline task runner
  pyproject.toml                    # Python package (oakbox CLI + deps)
  oakbox/                           # Orchestrator package
    state.py
    tools.py
    context.py
    agents.py
    pipeline.py
    cli.py
  .oakbox/
    agents/                         # Agent system prompts (architect, planner, ...)
    instructions/                   # Coding standards per technology
    status/                         # FEAT-NNN-slug.yaml — one per feature
    memory/                         # decisions.md, patterns.md, gotchas.md, context.md
    templates/
      feature-request.yaml          # Blank feature template
  src/                              # Application source (created per feature)
  tests/                            # Test suite (created per feature)
  docker/                           # Dockerfiles & compose (created per feature)
  docs/                             # Documentation output
```

---

## Code Conventions

Detailed style guides live in `.oakbox/instructions/` and are automatically
included in each agent's context.

| Guide | File | Covers |
|-------|------|--------|
| Python | `python.md` | uv, ruff, pytest, naming, types |
| React / TypeScript | `react.md` | npm, ESLint, Vitest, components, hooks |
| Docker | `docker.md` | Dockerfiles, Compose, multi-stage, security |
| Market Analysis UI/UX | `frontend-market-analysis.md` | App shell, components, a11y |
| Political Trades Analysis | `political-trades-analysis.md` | Portfolio tracking, scoring |

**Package managers:** `uv` (Python), `npm` (frontend). No alternatives.
**Task runner:** GNU Make — run `make help` to list all targets.
**Model override:** set `OAKBOX_MODEL` env var (default: `claude-sonnet-4-6`).

---

## Make Targets (Pipeline)

| Target | Usage |
|--------|-------|
| `make feature-new` | `make feature-new ID=001 TITLE="title" DESC="description"` |
| `make feature-run` | `make feature-run ID=001` |
| `make feature-run-from` | `make feature-run-from ID=001 FROM=coder` |
| `make feature-status` | `make feature-status ID=001` |
| `make feature-list` | `make feature-list` |

---

## Memory System

Four persistent files store cross-feature knowledge:

| File | Contents |
|------|---------|
| `decisions.md` | Architectural choices and rationale |
| `patterns.md` | Reusable code patterns and conventions |
| `gotchas.md` | Pitfalls, bugs, and workarounds |
| `context.md` | Current system shape — services, conventions, state |

The Memory agent reads and writes these directly. All other agents receive the
relevant files as read-only context at the start of each phase.
