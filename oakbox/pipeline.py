"""Pipeline runner — drives the agent sequence for a feature."""

from __future__ import annotations

import sys
from pathlib import Path

from . import agents, state

MEMORY_DIR = Path(__file__).parent.parent / ".oakbox" / "memory"
DOCS_DIR = Path(__file__).parent.parent / "docs"

_MEMORY_KEY_TO_FILE = {
    "decisions": MEMORY_DIR / "decisions.md",
    "patterns": MEMORY_DIR / "patterns.md",
    "gotchas": MEMORY_DIR / "gotchas.md",
    "context": MEMORY_DIR / "context.md",
    # memory phase uses _to_add suffix
    "decisions_to_add": MEMORY_DIR / "decisions.md",
    "patterns_to_add": MEMORY_DIR / "patterns.md",
    "gotchas_to_add": MEMORY_DIR / "gotchas.md",
    "context_to_add": MEMORY_DIR / "context.md",
}


def run(feature: dict, from_phase: str | None = None) -> dict:
    """Execute the pipeline, advancing through pending phases until complete or blocked."""
    feat_id = feature["id"]

    while True:
        phase = state.next_pending(feature)

        if phase is None:
            if state.is_complete(feature):
                _log(feat_id, "Pipeline complete.")
            else:
                _log(feat_id, "No pending phases but pipeline not complete — check state.")
            break

        # Honor --from-phase: skip phases that come before it
        if from_phase and state.PHASES.index(phase) < state.PHASES.index(from_phase):
            _log(feat_id, f"Skipping '{phase}' (before --from-phase={from_phase})")
            state.done(feature, phase, feature["phases"][phase].get("output"))
            state.save(feature)
            continue

        _log(feat_id, f"▶ Phase: {phase}")
        state.start(feature, phase)
        state.save(feature)

        try:
            output = agents.run_phase(feature, phase)
        except Exception as exc:  # noqa: BLE001
            reason = str(exc)
            state.block(feature, phase, reason)
            state.save(feature)
            _log(feat_id, f"✗ Blocked at '{phase}': {reason}", error=True)
            break

        # --- Tester verdict ---
        if phase == "tester":
            verdict = (output or {}).get("verdict", "pass")
            if verdict == "fail":
                state.done(feature, "tester", output)
                _flush_memory(output)
                if state.reenter_coder(feature):
                    count = feature["phases"]["coder"]["re_entry_count"]
                    _log(feat_id, f"✗ Tests failed — re-entering Coder (attempt {count}/3)")
                    state.save(feature)
                    continue
                else:
                    failure = (output or {}).get("failure_summary", "repeated test failures")
                    state.block(feature, "tester", f"Max re-entries reached: {failure}")
                    state.save(feature)
                    _log(feat_id, "✗ Blocked: max Coder re-entries (3) reached.", error=True)
                    break

        state.done(feature, phase, output)
        _flush_memory(output)

        if phase == "docs":
            _write_docs(output)

        state.save(feature)
        _log(feat_id, f"✓ Phase '{phase}' done.")

    return feature


# ---------------------------------------------------------------------------
# Memory flushing
# ---------------------------------------------------------------------------

def _flush_memory(output: dict | None) -> None:
    """Append any memory_updates from this phase's output to the memory files."""
    if not output:
        return
    updates = output.get("memory_updates") or {}
    if not updates:
        return

    for key, entries in updates.items():
        path = _MEMORY_KEY_TO_FILE.get(key)
        if not path or not entries:
            continue
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        additions = "\n\n".join(str(e) for e in entries if e)
        if additions:
            path.write_text(
                existing.rstrip() + "\n\n" + additions + "\n",
                encoding="utf-8",
            )

    # Memory phase may also have `new_entries` from the agent writing files directly
    new_entries = output.get("new_entries") or {}
    for key, entries in new_entries.items():
        path = _MEMORY_KEY_TO_FILE.get(key) or _MEMORY_KEY_TO_FILE.get(key + "_to_add")
        if not path or not entries:
            continue
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        additions = "\n\n".join(str(e) for e in entries if e)
        if additions:
            path.write_text(
                existing.rstrip() + "\n\n" + additions + "\n",
                encoding="utf-8",
            )


# ---------------------------------------------------------------------------
# Docs output
# ---------------------------------------------------------------------------

def _write_docs(output: dict | None) -> None:
    if not output:
        return
    DOCS_DIR.mkdir(exist_ok=True)
    for doc in output.get("documents", []):
        filename = doc.get("filename", "")
        content = doc.get("content", "")
        if not filename or not content:
            continue
        path = Path(filename)
        if not path.is_absolute():
            path = (Path(__file__).parent.parent / filename).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # Append index entries to docs/_index.md
    index_entries = output.get("index_entries", [])
    if index_entries:
        index_path = DOCS_DIR / "_index.md"
        existing = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Documentation Index\n"
        additions = "\n".join(str(e) for e in index_entries if e)
        if additions:
            index_path.write_text(existing.rstrip() + "\n" + additions + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _log(feat_id: str, msg: str, error: bool = False) -> None:
    line = f"[FEAT-{feat_id}] {msg}"
    if error:
        print(line, file=sys.stderr, flush=True)
    else:
        print(line, flush=True)
