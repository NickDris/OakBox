"""Assembles the user message sent to each agent."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
OAKBOX_DIR = REPO_ROOT / ".oakbox"
AGENTS_DIR = OAKBOX_DIR / "agents"
INSTRUCTIONS_DIR = OAKBOX_DIR / "instructions"
MEMORY_DIR = OAKBOX_DIR / "memory"

# Which memory files each phase reads
_MEMORY: dict[str, list[str]] = {
    "architect": ["decisions.md", "context.md"],
    "planner": ["decisions.md", "patterns.md", "gotchas.md", "context.md"],
    "coder": ["patterns.md", "gotchas.md", "context.md"],
    "tester": ["patterns.md", "gotchas.md"],
    "memory": ["decisions.md", "patterns.md", "gotchas.md", "context.md"],
    "docs": ["context.md", "patterns.md"],
}

# Which instruction guides each phase receives
_GUIDES: dict[str, list[str]] = {
    "architect": ["python.md", "react.md", "docker.md"],
    "planner": ["python.md", "react.md", "docker.md"],
    "coder": ["python.md", "react.md", "docker.md",
              "frontend-market-analysis.md", "political-trades-analysis.md"],
    "tester": ["python.md", "react.md"],
    "memory": [],
    "docs": [],
}

# Phases that can write files / run commands
WRITE_PHASES = {"coder", "tester", "memory", "docs"}

# Output schemas sent to each agent so they know what to put in complete()
_SCHEMAS: dict[str, str] = {
    "architect": """\
system_design:
  overview: "High-level description of the design"
  components:
    - name: "ComponentName"
      type: backend|frontend|database|infrastructure
      description: "What it does"
      technology: "Python/React/PostgreSQL/Docker/etc"
      location: "src/path/to/"
  apis:
    - method: GET|POST|PUT|DELETE|PATCH
      path: "/api/endpoint"
      description: "What it does"
      request_body: "Schema description or null"
      response: "Schema description"
      status_codes: [200, 400, 404]
  data_models:
    - name: "ModelName"
      table: "table_name"
      fields:
        - name: "field_name"
          type: "varchar(255)|int|bool|timestamp|etc"
          constraints: "primary key|unique|not null|etc"
  file_plan:
    - path: "src/path/to/file.py"
      action: create|modify
      description: "One-line description of change"
  component_interactions: "How components talk to each other"
assumptions:
  - "Assumption made"
risks:
  - description: "Risk description"
    mitigation: "How to handle it"
memory_updates:
  decisions:
    - "Architectural decision made"
  context:
    - "Project context to persist"
""",

    "planner": """\
tasks:
  - id: 1
    title: "Short task title"
    files:
      - path: "src/path/to/file.py"
        action: create|modify
    description: "Imperative description of what to implement"
    acceptance_criteria:
      - "Specific, measurable, testable criterion"
    dependencies: []   # list of task IDs this depends on
    layer: backend|frontend|database|infrastructure|testing
memory_updates:
  patterns:
    - "Reusable pattern or convention noted"
""",

    "coder": """\
completed:
  - task_id: 1
    status: done|blocked
    blocked_reason: null   # string if blocked, else null
    files_changed:
      - path: "src/path/to/file.py"
        action: created|modified
new_dependencies:
  - "package>=version"
deviations:
  - "Any deviation from the plan and why"
summary: "Brief summary of what was implemented"
memory_updates:
  patterns:
    - "## Pattern: Title\\n- **Context:** ...\\n- **Implementation:** ...\\n- **First used:** FEAT-<id>"
  gotchas:
    - "## Gotcha: Title\\n- **Problem:** ...\\n- **Cause:** ...\\n- **Fix:** ...\\n- **Discovered:** FEAT-<id>"
""",

    "tester": """\
results:
  - task_id: 1
    criterion: "Exact criterion text from plan"
    test_file: "tests/path/to/test_file.py"   # null if non-code check
    test_name: "test_function_name"            # null if non-code check
    test_type: unit|integration|e2e|lint|typecheck
    passed: true
    notes: null   # details if failed: expected vs actual, reproduce command
summary:
  total: 0
  passed: 0
  failed: 0
verdict: pass|fail
failure_summary: null   # string describing failures if verdict is fail
memory_updates:
  gotchas:
    - "## Gotcha: Title\\n- **Problem:** ...\\n- **Cause:** ...\\n- **Fix:** ...\\n- **Discovered:** FEAT-<id>"
""",

    "memory": """\
new_entries:
  decisions:
    - |
      ## FEAT-<id>: <Title> (<date>)
      - **Decision:** What was decided
      - **Rationale:** Why
      - **Alternatives considered:** What else was discussed
  patterns:
    - |
      ## Pattern: <Name>
      - **Tags:** #tag1 #tag2
      - **Context:** When to use this
      - **Implementation:** Code snippet or approach
      - **First used:** FEAT-<id>
  gotchas:
    - |
      ## Gotcha: <Title>
      - **Tags:** #tag1
      - **Problem:** What went wrong
      - **Cause:** Root cause
      - **Fix:** How to avoid it
      - **Discovered:** FEAT-<id>
  context:
    - "New project-wide fact or architectural change to persist"
updated_files:
  - "decisions.md"
summary: "What was recorded and why"
""",

    "docs": """\
documents:
  - filename: "docs/feature-slug.md"
    title: "Document Title"
    content: |
      # Title

      ## Overview
      ...
index_entries:
  - "- [Title](feature-slug.md) — one-line description"
summary: "What was documented"
""",
}

# Phase-specific instructions injected into the user message
_INSTRUCTIONS: dict[str, str] = {
    "architect": (
        "Analyze the feature request thoroughly. Read existing code in `src/` before designing "
        "so your design integrates with what already exists. Keep the design minimal — solve the "
        "request, nothing more. Document all assumptions."
    ),
    "planner": (
        "Decompose the Architect's design into atomic, ordered tasks. Every file from the "
        "Architect's file_plan must appear in at least one task. Make acceptance criteria "
        "specific and measurable — each one must be verifiable by running code or commands. "
        "Include a final integration verification task. Dependencies must form a DAG."
    ),
    "coder": (
        "Implement each task in order. Read existing files before modifying them. "
        "Run `uv run ruff check` on Python files and `npx tsc --noEmit` on TypeScript files "
        "before calling complete(). If a task is ambiguous, mark it blocked with a clear reason — "
        "do not guess. Fix only what the plan specifies; do not refactor unrelated code."
    ),
    "tester": (
        "Write and run a test for every acceptance criterion in the plan. "
        "Tests must be placed in `tests/` (Python) or `src/**/__tests__/` (React). "
        "Run tests with `uv run pytest` or `npm run test`. "
        "If all pass, verdict is 'pass'. If any fail, verdict is 'fail' and describe "
        "each failure precisely so the Coder can fix without guessing."
    ),
    "memory": (
        "Review every section of the feature output. Record only genuinely useful entries — "
        "no filler. Check existing memory files first to avoid duplicates. "
        "Update `.oakbox/memory/decisions.md`, `patterns.md`, `gotchas.md`, and `context.md` "
        "by reading each file and appending new entries. Write the files directly."
    ),
    "docs": (
        "Read the actual code files, not just the design. Write documentation that matches "
        "what was implemented. Use real code examples. Keep it scannable — developers prefer "
        "concise docs over walls of text. Write files directly to `docs/`. "
        "Update `docs/_index.md` with links to new docs."
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def system_prompt(phase: str) -> str:
    path = AGENTS_DIR / f"{phase}.md"
    return path.read_text(encoding="utf-8")


def user_message(feature: dict, phase: str) -> str:
    parts: list[str] = []

    # 1. Feature request
    parts.append(
        f"# Feature: FEAT-{feature['id']} — {feature['title']}\n\n"
        f"{feature['description']}"
    )

    # 2. Previous phase outputs
    phases_order = ["architect", "planner", "coder", "tester", "memory", "docs"]
    phase_idx = phases_order.index(phase)
    prev_outputs = []
    for prev in phases_order[:phase_idx]:
        output = feature["phases"][prev].get("output")
        if output:
            prev_outputs.append(
                f"### {prev.title()} Output\n\n```yaml\n"
                + yaml.dump(output, sort_keys=False, allow_unicode=True)
                + "```"
            )
    if prev_outputs:
        parts.append("# Previous Phase Outputs\n\n" + "\n\n".join(prev_outputs))

    # 3. Memory context
    mem_parts = []
    for fname in _MEMORY.get(phase, []):
        fpath = MEMORY_DIR / fname
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8").strip()
            if content:
                mem_parts.append(f"### {fname}\n\n{content}")
    if mem_parts:
        parts.append("# Memory Context\n\n" + "\n\n".join(mem_parts))

    # 4. Instruction guides
    guide_parts = []
    for fname in _GUIDES.get(phase, []):
        fpath = INSTRUCTIONS_DIR / fname
        if fpath.exists():
            guide_parts.append(f"### {fname}\n\n{fpath.read_text(encoding='utf-8')}")
    if guide_parts:
        parts.append("# Coding Standards\n\n" + "\n\n".join(guide_parts))

    # 5. Phase instructions + output schema
    schema = _SCHEMAS[phase]
    instructions = _INSTRUCTIONS[phase]
    parts.append(
        f"# Your Task\n\n{instructions}\n\n"
        "## Output Contract\n\n"
        "When you have finished, call the `complete` tool with an `output` object "
        "matching this schema exactly:\n\n"
        f"```yaml\n{schema}```\n\n"
        "Call `complete` exactly once, at the very end."
    )

    return "\n\n---\n\n".join(parts)
