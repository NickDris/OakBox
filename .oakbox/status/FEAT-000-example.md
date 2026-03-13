# FEAT-000: Example Feature (Scaffolding Setup)

## Metadata

- **Requested:** 2026-03-13
- **Status:** complete
- **Coder re-entry count:** 0

## Pipeline Status

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| architect | done | 2026-03-13 | 2026-03-13 |
| planner | done | 2026-03-13 | 2026-03-13 |
| coder | done | 2026-03-13 | 2026-03-13 |
| tester | done | 2026-03-13 | 2026-03-13 |
| memory | done | 2026-03-13 | 2026-03-13 |
| docs | done | 2026-03-13 | 2026-03-13 |

---

## Request

**Description:**
Set up the OakBox AI-assisted development scaffolding with agent roles,
workflow pipeline, status tracking, and memory system.

**User story:**
As a developer, I want a structured AI agent pipeline, so that features are
implemented through a consistent, trackable workflow.

**Scope boundaries:**
Scaffolding only. No application code.

**Constraints:**
Must work with Claude Code. All state in markdown files in the repo.

---

## Architect Output

The scaffolding consists of:
- Agent prompt files defining each role's behavior
- A feature pipeline workflow specification
- Status file template for tracking feature execution
- Memory files for cross-feature knowledge persistence
- CLAUDE.md as the master playbook

All files are markdown. No runtime dependencies.

---

## Planner Output

### Task 1: Create directory structure
- **File(s):** `.oakbox/agents/`, `.oakbox/workflows/`, `.oakbox/status/`, `.oakbox/memory/`, `.oakbox/templates/`, `docs/`
- **Action:** create
- **Description:** Create all scaffolding directories.
- **Acceptance criteria:**
  - [x] All directories exist
- **Dependencies:** none

### Task 2: Create CLAUDE.md
- **File(s):** `CLAUDE.md`
- **Action:** create
- **Description:** Write the master playbook with agent roles, pipeline, and rules.
- **Acceptance criteria:**
  - [x] All 6 agents documented
  - [x] Pipeline order defined
  - [x] Skills matrix included
- **Dependencies:** Task 1

### Task 3: Create agent prompt files
- **File(s):** `.oakbox/agents/*.md`
- **Action:** create
- **Description:** Write prompt files for all 6 agents.
- **Acceptance criteria:**
  - [x] Each agent has role, inputs, instructions, constraints
- **Dependencies:** Task 1

### Task 4: Create workflow and templates
- **File(s):** `.oakbox/workflows/feature-pipeline.md`, `.oakbox/templates/feature-request.md`
- **Action:** create
- **Description:** Write pipeline spec and feature request template.
- **Acceptance criteria:**
  - [x] Pipeline phases and transitions documented
  - [x] Template has all required sections
- **Dependencies:** Task 1

### Task 5: Create memory seed files
- **File(s):** `.oakbox/memory/*.md`
- **Action:** create
- **Description:** Initialize memory files with format guides.
- **Acceptance criteria:**
  - [x] All 4 memory files exist with format documentation
- **Dependencies:** Task 1

---

## Coder Output

All files created as specified. No application code — scaffolding only.

Files created:
- `CLAUDE.md`
- `.oakbox/agents/architect.md`
- `.oakbox/agents/planner.md`
- `.oakbox/agents/coder.md`
- `.oakbox/agents/tester.md`
- `.oakbox/agents/memory.md`
- `.oakbox/agents/docs.md`
- `.oakbox/workflows/feature-pipeline.md`
- `.oakbox/templates/feature-request.md`
- `.oakbox/memory/decisions.md`
- `.oakbox/memory/patterns.md`
- `.oakbox/memory/gotchas.md`
- `.oakbox/memory/context.md`

---

## Tester Output

### Test Results Summary
- Total criteria: 6
- Passed: 6
- Failed: 0

All scaffolding files exist and contain the required sections.

---

## Memory Output

Recorded initial architectural decision about file-based pipeline in
`.oakbox/memory/decisions.md`. Updated `.oakbox/memory/context.md` with
project state.

---

## Docs Output

Created `docs/_index.md` as the documentation root. Full documentation
will be generated as application features are built.
