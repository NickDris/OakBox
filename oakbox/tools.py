"""Tool definitions and execution for agent tool-use loops."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Tool schemas (Anthropic tool format)
# ---------------------------------------------------------------------------

READ_TOOLS: list[dict] = [
    {
        "name": "read_file",
        "description": "Read the contents of a file in the repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relative to repo root."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_directory",
        "description": "List the immediate contents of a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path relative to repo root."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "search_files",
        "description": "Search for a text pattern across files using grep.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Text or regex to search for."},
                "path": {"type": "string", "description": "Directory to search in (relative). Defaults to '.'"},
                "include": {"type": "string", "description": "File glob filter, e.g. '*.py'. Defaults to all files."},
            },
            "required": ["pattern"],
        },
    },
]

WRITE_TOOLS: list[dict] = [
    {
        "name": "write_file",
        "description": "Write content to a file, creating parent directories as needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relative to repo root."},
                "content": {"type": "string", "description": "Full file content to write."},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_command",
        "description": (
            "Run an allowed shell command from the repo root. "
            "Allowed prefixes: 'uv run ruff', 'uv run pytest', 'uv run mypy', "
            "'npx tsc', 'npm run', 'make lint', 'make test', 'make typecheck'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to run."},
            },
            "required": ["command"],
        },
    },
]

COMPLETE_TOOL: dict = {
    "name": "complete",
    "description": "Signal task completion and provide structured output. Call this exactly once when done.",
    "input_schema": {
        "type": "object",
        "properties": {
            "output": {
                "type": "object",
                "description": "Structured output object for this phase.",
            },
        },
        "required": ["output"],
    },
}

_ALLOWED_COMMAND_PREFIXES = (
    "uv run ruff",
    "uv run pytest",
    "uv run mypy",
    "npx tsc",
    "npm run",
    "make lint",
    "make test",
    "make typecheck",
    "make format",
)


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def execute(name: str, inputs: dict[str, Any], allow_write: bool) -> str:
    try:
        if name == "read_file":
            return _read_file(inputs["path"])
        if name == "list_directory":
            return _list_directory(inputs["path"])
        if name == "search_files":
            return _search_files(
                inputs["pattern"],
                inputs.get("path", "."),
                inputs.get("include"),
            )
        if name == "write_file":
            if not allow_write:
                return "Error: write_file not permitted for this phase."
            return _write_file(inputs["path"], inputs["content"])
        if name == "run_command":
            if not allow_write:
                return "Error: run_command not permitted for this phase."
            return _run_command(inputs["command"])
        return f"Error: unknown tool '{name}'"
    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"


def _read_file(rel_path: str) -> str:
    path = _safe_path(rel_path)
    if not path.exists():
        return f"Error: file not found: {rel_path}"
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: binary file, cannot read as text: {rel_path}"


def _list_directory(rel_path: str) -> str:
    path = _safe_path(rel_path)
    if not path.exists():
        return f"Error: directory not found: {rel_path}"
    entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    lines = []
    for e in entries:
        prefix = "  " if e.is_file() else "/"
        lines.append(f"{prefix}{e.name}")
    return "\n".join(lines) if lines else "(empty)"


def _search_files(pattern: str, search_path: str, include: str | None) -> str:
    base = _safe_path(search_path)
    cmd = ["grep", "-r", "-n", "--include", include or "*", pattern, str(base)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    output = result.stdout.strip()
    # Make paths relative to repo root for readability
    output = output.replace(str(REPO_ROOT) + "/", "")
    return output or "No matches found."


def _write_file(rel_path: str, content: str) -> str:
    path = _safe_path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"Written: {rel_path} ({len(content)} bytes)"


def _run_command(command: str) -> str:
    stripped = command.strip()
    if not any(stripped.startswith(p) for p in _ALLOWED_COMMAND_PREFIXES):
        return (
            f"Error: command not allowed: '{stripped}'. "
            f"Allowed prefixes: {', '.join(_ALLOWED_COMMAND_PREFIXES)}"
        )
    result = subprocess.run(
        stripped,
        shell=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=180,
    )
    parts = []
    if result.stdout:
        parts.append(f"stdout:\n{result.stdout}")
    if result.stderr:
        parts.append(f"stderr:\n{result.stderr}")
    parts.append(f"exit_code: {result.returncode}")
    return "\n".join(parts)


def _safe_path(rel_path: str) -> Path:
    path = (REPO_ROOT / rel_path).resolve()
    if not str(path).startswith(str(REPO_ROOT)):
        raise ValueError(f"Path escapes repo root: {rel_path}")
    return path
