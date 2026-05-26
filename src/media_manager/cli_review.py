"""CLI for review sessions — save, load, and apply review decisions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _emit_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _error_json(message: str) -> dict:
    return {"status": "error", "message": message}


def cmd_save_session(args: argparse.Namespace) -> int:
    session_path = Path(args.session_path)
    decisions = {}
    if args.decisions:
        try:
            decisions = json.loads(args.decisions)
        except json.JSONDecodeError as exc:
            payload = _error_json(f"Invalid decisions JSON: {exc}")
            if args.json:
                _emit_json(payload)
            else:
                print(f"Error: Invalid decisions JSON: {exc}", file=sys.stderr)
            return 1

    session_data = {
        "schema_version": 1,
        "source_kind": args.source_kind,
        "decisions": decisions,
        "decision_count": len(decisions),
    }

    try:
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(json.dumps(session_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        payload = _error_json(f"Failed to write session: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: Failed to write session: {exc}", file=sys.stderr)
        return 1

    payload = {"status": "saved", "path": str(session_path), "decision_count": len(decisions)}
    if args.json:
        _emit_json(payload)
    else:
        print(f"Session saved: {session_path} ({len(decisions)} decisions)")
    return 0


def cmd_load_session(args: argparse.Namespace) -> int:
    session_path = Path(args.session_path)
    try:
        session_data = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception as exc:
        payload = _error_json(f"Failed to read session: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: Failed to read session: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _emit_json(session_data)
    else:
        decision_count = session_data.get("decision_count", 0)
        source_kind = session_data.get("source_kind", "unknown")
        print(f"Session: {session_path}")
        print(f"  Source kind: {source_kind}")
        print(f"  Decisions:   {decision_count}")
        decisions = session_data.get("decisions", {})
        for key, value in decisions.items():
            print(f"    {key}: {value}")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    to_remove = []
    if args.to_remove:
        for path_str in args.to_remove:
            to_remove.append(path_str)

    if not to_remove:
        payload = _error_json("No files specified for removal. Use --to-remove.")
        if args.json:
            _emit_json(payload)
        else:
            print("Error: No files specified for removal.", file=sys.stderr)
        return 1

    if not args.yes:
        if args.json:
            _emit_json({"status": "aborted", "reason": "confirmation required (-y / --yes)"})
        else:
            print("Use --yes to confirm deletion of the listed files.")
            for path in to_remove:
                print(f"  Would remove: {path}")
        return 1

    import send2trash
    removed = 0
    errors = []
    for path_str in to_remove:
        try:
            send2trash.send2trash(path_str)
            removed += 1
        except Exception as exc:
            errors.append({"path": path_str, "error": str(exc)})

    payload = {"status": "applied", "removed": removed, "errors": errors}
    if args.json:
        _emit_json(payload)
    else:
        print(f"Removed: {removed} files")
        for err in errors:
            print(f"  Error: {err['path']} — {err['error']}", file=sys.stderr)
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager review",
        description="Manage review sessions: save decisions, load sessions, and apply cleanup.",
        epilog=(
            "Examples:\n"
            "  media-manager review save-session --session-path session.json --decisions '{\"key\": \"value\"}'\n"
            "  media-manager review load-session --session-path session.json\n"
            "  media-manager review apply --to-remove file1.jpg file2.jpg --yes\n"
            "  media-manager review apply --to-remove file1.jpg --yes --json\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="review_action")

    save_p = subparsers.add_parser("save-session", help="Save review decisions to a session file.")
    save_p.add_argument("--session-path", type=Path, required=True, help="Path for the session file.")
    save_p.add_argument("--decisions", help="JSON string of decisions, e.g. '{\"group_id\": \"keep_path\"}'.")
    save_p.add_argument("--source-kind", default="manual", help="Source kind label (default: manual).")
    save_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    load_p = subparsers.add_parser("load-session", help="Load review decisions from a session file.")
    load_p.add_argument("--session-path", type=Path, required=True, help="Path to the session file.")
    load_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    apply_p = subparsers.add_parser("apply", help="Apply review decisions: move files to trash.")
    apply_p.add_argument("--to-remove", nargs="*", default=[], help="One or more file paths to remove.")
    apply_p.add_argument("--yes", "-y", action="store_true", help="Confirm file removal.")
    apply_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    return parser


ACTION_HANDLERS = {
    "save-session": cmd_save_session,
    "load-session": cmd_load_session,
    "apply": cmd_apply,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.review_action is None:
        parser.print_help()
        return 0

    handler = ACTION_HANDLERS.get(args.review_action)
    if handler is None:
        print(f"Unknown review action: {args.review_action}", file=sys.stderr)
        return 1

    return handler(args)
