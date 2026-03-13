# Feature Pipeline — Execution Specification

## Overview

This document defines the exact sequence of operations when processing a feature
request through the OakBox agent pipeline.

## Pipeline Phases

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Architect   │───▶│   Planner   │───▶│    Coder    │
│  (design)    │    │  (tasks)    │    │   (build)   │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                             ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Docs      │◀───│   Memory    │◀───│   Tester    │
│ (document)   │    │  (record)   │    │  (verify)   │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                     ┌───────┴───────┐
                                     │  Tests fail?   │
                                     │  ──▶ Coder    │
                                     └───────────────┘
```

## Phase Transitions

### Valid status values

- `pending` — not yet started
- `in_progress` — currently executing
- `done` — completed successfully
- `blocked` — cannot proceed (requires intervention)

### Transition rules

1. Only ONE phase may be `in_progress` at any time.
2. A phase can only move to `in_progress` if all previous phases are `done`.
3. The only backward transition allowed: Tester → Coder (on test failure).
4. When Coder is re-entered, the Tester phase resets to `pending`.
5. Maximum re-entry cycles: 3. After 3 Tester→Coder loops, mark the feature
   as `blocked` and stop.

## Execution Protocol

### Step-by-step for the executing agent (Claude)

```
1. READ the status file for the target feature
2. FIND the first phase with status "pending"
3. IF no pending phase exists:
   - IF all phases are "done" → feature is COMPLETE
   - IF any phase is "blocked" → feature is BLOCKED, report to user
4. LOAD the agent prompt from .oakbox/agents/<phase>.md
5. FOLLOW the agent instructions exactly
6. WRITE outputs to the status file
7. UPDATE phase status
8. GOTO step 1
```

### Starting a new feature

```bash
# 1. Create the status file
cp .oakbox/templates/feature-request.md .oakbox/status/FEAT-<NNN>-<short-name>.md

# 2. Edit the Request section with the feature description

# 3. Execute the pipeline
#    Say: "Execute the feature pipeline for FEAT-<NNN>"
```

### Resuming a paused/blocked feature

```
1. Read the status file to understand where it stopped
2. Resolve the blocker (if any)
3. Set the blocked phase back to "pending"
4. Resume the pipeline from step 1 of the execution protocol
```

## Quality Gates

Each phase has implicit quality gates:

| Phase | Gate |
|-------|------|
| Architect | Design must cover all aspects of the request |
| Planner | Every architect component maps to at least one task |
| Coder | Code passes linting (ruff/tsc) |
| Tester | All acceptance criteria have corresponding tests |
| Memory | At least one memory file is updated |
| Docs | All new components/APIs are documented |

## Monitoring

The status file header contains a summary table that is updated after each
phase completes:

```markdown
| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| architect | done | 2024-01-15 10:00 | 2024-01-15 10:05 |
| planner | in_progress | 2024-01-15 10:06 | - |
| coder | pending | - | - |
| tester | pending | - | - |
| memory | pending | - | - |
| docs | pending | - | - |
```
