"""OakBox CLI — create and run feature pipelines."""

from __future__ import annotations

import argparse
import sys

from . import state, pipeline


def cmd_new(args: argparse.Namespace) -> None:
    feature = state.create(args.id, args.title, args.description or "")
    yaml_path = next(
        (state.STATUS_DIR / p for p in state.STATUS_DIR.iterdir()
         if p.name.startswith(f"FEAT-{args.id}-")),
        state.STATUS_DIR,
    )
    print(f"Created FEAT-{args.id}: {args.title}")
    print(f"Status file: {state._find(args.id)}")


def cmd_run(args: argparse.Namespace) -> None:
    feature = state.load(args.id)
    if state.is_complete(feature):
        print(f"[FEAT-{args.id}] Already complete. Use --from-phase to re-run a phase.")
        sys.exit(0)
    if state.is_blocked(feature) and not args.from_phase:
        blocked = [
            (p, d.get("blocked_reason", ""))
            for p, d in feature["phases"].items()
            if d["status"] == "blocked"
        ]
        for p, reason in blocked:
            print(f"[FEAT-{args.id}] Blocked at '{p}': {reason}", file=sys.stderr)
        print("Resolve the blocker, then re-run with --from-phase to resume.", file=sys.stderr)
        sys.exit(1)
    pipeline.run(feature, from_phase=args.from_phase)


def cmd_status(args: argparse.Namespace) -> None:
    feature = state.load(args.id)
    print(f"\nFEAT-{feature['id']} — {feature['title']}")
    print(f"{'Phase':<12} {'Status':<15} {'Re-entries':<12} Completed")
    print("─" * 62)
    for phase_name in state.PHASES:
        d = feature["phases"][phase_name]
        status = d["status"]
        completed = (d.get("completed_at") or "")[:19]
        re_entries = str(d["re_entry_count"]) if "re_entry_count" in d else ""
        blocked_note = f"  ← {d.get('blocked_reason', '')}" if status == "blocked" else ""
        print(f"{phase_name:<12} {status:<15} {re_entries:<12} {completed}{blocked_note}")
    print()


def cmd_list(args: argparse.Namespace) -> None:
    import yaml as _yaml
    files = sorted(state.STATUS_DIR.glob("FEAT-*.yaml"))
    if not files:
        print("No features found.")
        return
    print(f"\n{'ID':<12} {'Title':<42} Current Phase")
    print("─" * 70)
    for path in files:
        try:
            feature = _yaml.safe_load(path.read_text())
            phase = state.next_pending(feature) or ("complete" if state.is_complete(feature) else "blocked")
            print(f"FEAT-{feature['id']:<7} {feature['title'][:40]:<42} {phase}")
        except Exception as exc:  # noqa: BLE001
            print(f"{path.name}: error ({exc})")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="oakbox",
        description="OakBox — AI-assisted feature development pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # oakbox new <id> <title> [--description TEXT]
    p_new = sub.add_parser("new", help="Create a new feature")
    p_new.add_argument("id", help="Feature ID (e.g. 001)")
    p_new.add_argument("title", help="Short title")
    p_new.add_argument("-d", "--description", default="", help="Full description")

    # oakbox run <id> [--from-phase PHASE]
    p_run = sub.add_parser("run", help="Run the pipeline for a feature")
    p_run.add_argument("id", help="Feature ID")
    p_run.add_argument(
        "--from-phase",
        choices=state.PHASES,
        default=None,
        help="Resume or restart from a specific phase",
    )

    # oakbox status <id>
    p_status = sub.add_parser("status", help="Show phase status for a feature")
    p_status.add_argument("id", help="Feature ID")

    # oakbox list
    sub.add_parser("list", help="List all features and their current phase")

    args = parser.parse_args()
    dispatch = {
        "new": cmd_new,
        "run": cmd_run,
        "status": cmd_status,
        "list": cmd_list,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
