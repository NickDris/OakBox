"""YAML-backed feature state management."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).parent.parent
STATUS_DIR = REPO_ROOT / ".oakbox" / "status"

PHASES = ["architect", "planner", "coder", "tester", "memory", "docs"]


# ---------------------------------------------------------------------------
# Load / save
# ---------------------------------------------------------------------------

def load(feat_id: str) -> dict:
    return yaml.safe_load(_find(feat_id).read_text())


def save(feature: dict) -> None:
    feature["updated"] = _now()
    _find(feature["id"]).write_text(
        yaml.dump(feature, sort_keys=False, allow_unicode=True, width=120)
    )


def _find(feat_id: str) -> Path:
    for p in STATUS_DIR.glob(f"FEAT-{feat_id}*.yaml"):
        return p
    raise FileNotFoundError(f"No feature file for ID: {feat_id}")


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create(feat_id: str, title: str, description: str) -> dict:
    slug = title.lower().replace(" ", "-")[:40]
    path = STATUS_DIR / f"FEAT-{feat_id}-{slug}.yaml"
    feature: dict[str, Any] = {
        "id": feat_id,
        "title": title,
        "description": description,
        "created": _now(),
        "updated": _now(),
        "phases": {
            phase: _blank_phase(phase)
            for phase in PHASES
        },
    }
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(feature, sort_keys=False, allow_unicode=True, width=120))
    return feature


def _blank_phase(phase: str) -> dict:
    base: dict[str, Any] = {
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "output": None,
    }
    if phase == "coder":
        base["re_entry_count"] = 0
    return base


# ---------------------------------------------------------------------------
# State transitions
# ---------------------------------------------------------------------------

def next_pending(feature: dict) -> str | None:
    for phase in PHASES:
        if feature["phases"][phase]["status"] == "pending":
            return phase
    return None


def start(feature: dict, phase: str) -> None:
    feature["phases"][phase]["status"] = "in_progress"
    feature["phases"][phase]["started_at"] = _now()


def done(feature: dict, phase: str, output: Any) -> None:
    feature["phases"][phase]["status"] = "done"
    feature["phases"][phase]["completed_at"] = _now()
    feature["phases"][phase]["output"] = output


def block(feature: dict, phase: str, reason: str) -> None:
    feature["phases"][phase]["status"] = "blocked"
    feature["phases"][phase]["blocked_reason"] = reason


def reenter_coder(feature: dict) -> bool:
    """Reset coder + tester to pending for another attempt. Returns False if max reached."""
    coder = feature["phases"]["coder"]
    if coder.get("re_entry_count", 0) >= 3:
        return False
    coder["re_entry_count"] = coder.get("re_entry_count", 0) + 1
    coder["status"] = "pending"
    coder["completed_at"] = None
    coder["output"] = None
    tester = feature["phases"]["tester"]
    tester["status"] = "pending"
    tester["started_at"] = None
    tester["completed_at"] = None
    tester["output"] = None
    return True


def is_complete(feature: dict) -> bool:
    return all(feature["phases"][p]["status"] == "done" for p in PHASES)


def is_blocked(feature: dict) -> bool:
    return any(feature["phases"][p]["status"] == "blocked" for p in PHASES)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
