"""Undo bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_undo <action>

Actions: preview | apply
Reads journal_path from stdin JSON.
Output: undo result JSON on stdout. Errors: JSON on stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.core.state.undo import execute_undo_journal

from media_manager.bridge_base import emit as _emit, fail as _fail, validate_app_path as _validate_app_path

logger = logging.getLogger(__name__)


def cmd_preview() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}")

    journal_path = payload.get("journal_path", "")
    if not journal_path:
        return _fail("journal_path is required.")
    try:
        journal_path = _validate_app_path(Path(journal_path))
    except ValueError as exc:
        return _fail(str(exc))

    try:
        logger.info("Starting undo preview: %s", journal_path)
        result = execute_undo_journal(journal_path, apply=False)
    except Exception as exc:
        logger.exception("Undo preview failed")
        return _fail(f"Undo preview failed: {exc}")

    output: dict = {
        "kind": "preview",
        "apply_requested": False,
        "journal_path": str(result.journal_path),
        "journal_command_name": result.journal_command_name,
        "original_apply_requested": result.original_apply_requested,
        "original_exit_code": result.original_exit_code,
        "entry_count": result.entry_count,
        "reversible_entry_count": result.reversible_entry_count,
        "planned_count": result.planned_count,
        "undone_count": result.undone_count,
        "skipped_count": result.skipped_count,
        "error_count": result.error_count,
        "status_summary": result.status_summary,
        "undo_action_summary": result.undo_action_summary,
        "reason_summary": result.reason_summary,
        "entries": [
            {
                "undo_action": e.undo_action,
                "source_path": str(e.source_path) if e.source_path else None,
                "target_path": str(e.target_path) if e.target_path else None,
                "status": e.status,
                "reason": e.reason,
            }
            for e in result.entries
        ],
    }
    _emit(output)
    return 0


def cmd_apply() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}")

    journal_path = payload.get("journal_path", "")
    if not journal_path:
        return _fail("journal_path is required.")
    try:
        journal_path = _validate_app_path(Path(journal_path))
    except ValueError as exc:
        return _fail(str(exc))

    try:
        logger.info("Starting undo apply: %s", journal_path)
        result = execute_undo_journal(journal_path, apply=True)
    except Exception as exc:
        logger.exception("Undo apply failed")
        return _fail(f"Undo apply failed: {exc}")

    output: dict = {
        "kind": "apply",
        "apply_requested": True,
        "journal_path": str(result.journal_path),
        "journal_command_name": result.journal_command_name,
        "original_apply_requested": result.original_apply_requested,
        "original_exit_code": result.original_exit_code,
        "entry_count": result.entry_count,
        "reversible_entry_count": result.reversible_entry_count,
        "planned_count": result.planned_count,
        "undone_count": result.undone_count,
        "skipped_count": result.skipped_count,
        "error_count": result.error_count,
        "status_summary": result.status_summary,
        "undo_action_summary": result.undo_action_summary,
        "reason_summary": result.reason_summary,
        "entries": [
            {
                "undo_action": e.undo_action,
                "source_path": str(e.source_path) if e.source_path else None,
                "target_path": str(e.target_path) if e.target_path else None,
                "status": e.status,
                "reason": e.reason,
            }
            for e in result.entries
        ],
    }
    _emit(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media_manager.bridge_undo",
        description="Undo bridge for Tauri desktop app.",
    )
    parser.add_argument("action", choices=["preview", "apply"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    if args.action == "preview":
        return cmd_preview()
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
