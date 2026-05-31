"""Review workbench bridge for the Tauri desktop app.

Manages review sessions: load scan data, record decisions, execute cleanup.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail, validate_app_path as _validate_app_path

logger = logging.getLogger(__name__)


def cmd_apply() -> int:
    """Apply review decisions: move files marked for removal to trash."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    to_remove = payload.get("to_remove", [])

    removed = 0
    errors = []
    import send2trash
    for path in to_remove:
        try:
            send2trash.send2trash(path)
            removed += 1
        except (OSError, RuntimeError) as e:
            logger.error("Review apply: failed to trash %s: %s", path, e)
            errors.append(str(e))

    _emit({"status": "applied", "removed": removed, "errors": errors})
    return 0


def cmd_save_session() -> int:
    """Save review decisions to a session file."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    session_path = Path(payload.get("session_path", ""))
    if not str(session_path):
        return _fail("session_path is required.")
    try:
        session_path = _validate_app_path(session_path)
    except ValueError as exc:
        return _fail(str(exc))

    decisions = payload.get("decisions", {})
    source_kind = payload.get("source_kind", "exact")

    session_data = {
        "schema_version": 1,
        "source_kind": source_kind,
        "decisions": decisions,
        "decision_count": len(decisions),
    }

    try:
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(json.dumps(session_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except (OSError, ValueError) as exc:
        logger.error("Review: failed to save session: %s", exc)
        return _fail(f"Failed to write session: {exc}")

    _emit({"status": "saved", "path": str(session_path), "decision_count": len(decisions)})
    return 0


def cmd_load_session() -> int:
    """Load review decisions from a session file."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    session_path = Path(payload.get("session_path", ""))
    if not str(session_path):
        return _fail("session_path is required.")
    try:
        session_path = _validate_app_path(session_path)
    except ValueError as exc:
        return _fail(str(exc))

    try:
        session_data = json.loads(session_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        logger.error("Review: failed to load session: %s", exc)
        return _fail(f"Failed to read session: {exc}")

    _emit(session_data)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_review",
        description="Review workbench bridge for Tauri desktop app.",
    )
    parser.add_argument("action", choices=["save-session", "load-session", "apply"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    if args.action == "save-session":
        logger.info("Review: saving session")
        return cmd_save_session()
    if args.action == "apply":
        logger.info("Review: applying decisions")
        return cmd_apply()
    logger.info("Review: loading session")
    return cmd_load_session()


if __name__ == "__main__":
    raise SystemExit(main())
