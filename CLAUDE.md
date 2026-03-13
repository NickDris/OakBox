# OakBox — AI-Assisted Web Development Scaffolding

## Project Overview

OakBox is a structured, multi-agent AI development workflow. When a feature is
requested, a pipeline of specialized agents executes in sequence. Each agent
follows the plan blindly, updates execution status, and hands off to the next.

**Tech stack skills:** Python 3.12, React (TypeScript), Docker, PostgreSQL

---

## Agent Team & Execution Order

Every feature request triggers this pipeline in strict order:

| # | Agent | Role | Prompt file |
|---|-------|------|-------------|
| 1 | **Architect** | Designs system-level approach, defines components, APIs, data models | `.oakbox/agents/architect.md` |
| 2 | **Feature Planner** | Breaks the architect's design into ordered, atomic tasks with acceptance criteria | `.oakbox/agents/planner.md` |
| 3 | **Coder** | Implements each task from the plan, writing production code | `.oakbox/agents/coder.md` |
| 4 | **Tester** | Writes and runs tests, validates acceptance criteria, reports failures back | `.oakbox/agents/tester.md` |
| 5 | **Memory** | Records decisions, patterns, gotchas, and project context for future agents | `.oakbox/agents/memory.md` |
| 6 | **Tech Doc Writer** | Produces user-facing and developer-facing documentation | `.oakbox/agents/docs.md` |

---

## How the Workflow Runs

### Triggering a feature

Create a new file in `.oakbox/status/` using the template:

```bash
cp .oakbox/templates/feature-request.md .oakbox/status/FEAT-<id>-<short-name>.md
```

Then fill in the **Request** section and invoke the pipeline (see below).

### Pipeline execution

When executing a feature, follow these rules **exactly**:

1. **Read** `.oakbox/status/FEAT-<id>-<short-name>.md` to get the current state.
2. **Identify** which agent phase is `status: pending` (the next to run).
3. **Load** that agent's prompt from `.oakbox/agents/<agent>.md`.
4. **Execute** the agent's instructions. Write all outputs into the designated
   sections of the status file.
5. **Update** the phase status to `done` with a timestamp.
6. **Proceed** to the next pending phase. Repeat until all phases are `done`.

### Status file is the single source of truth

- Never skip a phase.
- Never modify a phase marked `done`.
- If a phase fails, mark it `blocked` with a reason and stop the pipeline.
- The Tester agent may send the pipeline back to Coder (mark Coder as `pending`
  again) if tests fail — this is the only allowed backward jump.

---

## Agent Skills Matrix

| Skill | Architect | Planner | Coder | Tester | Memory | Docs |
|-------|-----------|---------|-------|--------|--------|------|
| Python 3.12 | design | plan | write | test | - | document |
| React / TypeScript | design | plan | write | test | - | document |
| Docker | design | plan | write | test | - | document |
| PostgreSQL | design | plan | - | test | - | document |
| API design (REST/GraphQL) | design | plan | write | test | - | document |
| Feature implementation | - | plan | write | - | - | - |
| Troubleshooting / debugging | diagnose | - | fix | reproduce | record | - |
| CI/CD | design | plan | write | validate | - | document |

---

## Code Conventions & Style Guides

Detailed, unambiguous conventions for each skill area live in `.oakbox/instructions/`.
Agents **must** read and follow the relevant guide(s) before writing any code.

| Guide | File | Covers |
|-------|------|--------|
| **Python** | `.oakbox/instructions/python.md` | uv, ruff, pytest, naming, types, project layout |
| **React / TypeScript** | `.oakbox/instructions/react.md` | npm, ESLint, Vitest, components, hooks, state |
| **Docker** | `.oakbox/instructions/docker.md` | Dockerfiles, Compose, multi-stage builds, security |
| **Market Analysis UI/UX** | `.oakbox/instructions/frontend-market-analysis.md` | App shell, page wireframes, component library, data types, a11y |

### DevOps

- **Package managers:** `uv` (Python), `npm` (frontend). No alternatives.
- **Task runner:** GNU Make — see `Makefile` at project root.
- Run `make help` to list all available targets.

---

## Directory Layout

```
OakBox/
  CLAUDE.md                        # This file — the master playbook
  Makefile                         # DevOps task runner (lint, test, build, docker)
  .oakbox/
    agents/                        # Agent role prompts
      architect.md
      planner.md
      coder.md
      tester.md
      memory.md
      docs.md
    instructions/                  # Code conventions & style guides
      python.md                    # Python 3.12, uv, ruff, pytest
      react.md                     # React, TypeScript, npm, Vitest
      docker.md                    # Docker, Compose, multi-stage builds
      frontend-market-analysis.md  # Market analysis app UI/UX spec
    workflows/
      feature-pipeline.md          # Detailed pipeline spec
    status/                        # One file per feature (execution state)
      FEAT-000-example.md          # Example status file
    memory/
      decisions.md                 # Architectural decisions log
      patterns.md                  # Reusable patterns & snippets
      gotchas.md                   # Known pitfalls & workarounds
      context.md                   # Project-wide context for agents
    templates/
      feature-request.md           # Blank feature template
  docs/                            # Generated documentation output
    _index.md                      # Docs index
  src/                             # Application source (created per feature)
  tests/                           # Test suite (created per feature)
  docker/                          # Dockerfiles & compose (created per feature)
```

---

## Rules for All Agents

1. **Read your prompt file** (`.oakbox/agents/<role>.md`) before acting.
2. **Read the status file** for the current feature before doing any work.
3. **Read the relevant instruction guides** (`.oakbox/instructions/`) before writing code.
4. **Write your outputs** into the status file under your designated section.
5. **Update phase status** immediately when you start (`in_progress`) and finish (`done`).
6. **Never deviate** from the plan produced by the previous agent in the chain.
7. **Record blockers** — if you cannot proceed, mark your phase `blocked` with a
   clear reason and stop.
8. **Check `.oakbox/memory/`** before starting — past decisions and gotchas apply.
9. **Append to `.oakbox/memory/`** if you discover something future agents should know.
10. **Use `make` targets** for lint, test, build, and docker operations.

---

## Quick Start

To process a new feature request:

```
1. cp .oakbox/templates/feature-request.md .oakbox/status/FEAT-001-my-feature.md
2. Edit the Request section with the feature description
3. Run the pipeline: execute each agent in order (Architect → Planner → Coder → Tester → Memory → Docs)
4. Monitor progress in the status file
```
