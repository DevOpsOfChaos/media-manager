"""Review workbench bridge for the Tauri desktop app.

Manages review sessions: load scan data, record decisions, execute cleanup.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_app_dir() -> Path:
    return Path(os.environ.get("MEDIA_MANAGER_HOME", Path.home() / ".media-manager")).resolve()


def _validate_app_path(path: Path) -> Path:
    app_dir = _get_app_dir()
    resolved = path.resolve()
    if not str(resolved).startswith(str(app_dir)):
        raise ValueError(f"Path {resolved} is outside app directory {app_dir}")
    return resolved


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


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
    except Exception as exc:
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
    except Exception as exc:
        logger.error("Review: failed to load session: %s", exc)
        return _fail(f"Failed to read session: {exc}")

    _emit(session_data)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_review",
        description="Review workbench bridge for Tauri desktop app.",
    )
    parser.add_argument("action", choices=["save-session", "load-session"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    if args.action == "save-session":
        logger.info("Review: saving session")
        return cmd_save_session()
    logger.info("Review: loading session")
    return cmd_load_session()


if __name__ == "__main__":
    raise SystemExit(main())
