"""Trip collection bridge for the Tauri desktop app.

Called by the Rust backend via subprocess:
    python -m media_manager.bridge_trip <preview|apply>

Reads trip options JSON from stdin.
Output: result JSON on stdout. Errors: JSON on stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.core.workflows import (
    TripWorkflowOptions,
    build_trip_dry_run,
    execute_trip_plan,
    parse_trip_date,
)

from media_manager.bridge_base import emit as _emit, fail as _fail

logger = logging.getLogger(__name__)


def _parse_options(payload: dict) -> TripWorkflowOptions:
    use_hardlinks = payload.get("use_hardlinks", True)
    target_root_str = payload.get("target_root", "")
    if not target_root_str:
        raise ValueError("target_root is required")

    return TripWorkflowOptions(
        source_dirs=tuple(Path(p) for p in payload.get("source_dirs", [])),
        target_root=Path(target_root_str),
        label=payload.get("label", "trip"),
        start_date=parse_trip_date(payload.get("start_date", "")),
        end_date=parse_trip_date(payload.get("end_date", "")),
        mode="link" if use_hardlinks else "copy",
        recursive=payload.get("recursive", True),
        include_hidden=payload.get("include_hidden", False),
    )


def cmd_preview() -> int:
    """Preview trip collection plan from stdin JSON options without moving files."""
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin.")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    try:
        options = _parse_options(payload)
    except (TypeError, ValueError, KeyError) as exc:
        logger.error("Trip preview: invalid options: %s", exc)
        return _fail(f"Invalid options: {exc}")

    try:
        logger.info("Starting trip plan preview: %s", options.label)
        plan = build_trip_dry_run(options)
    except (OSError, ValueError, RuntimeError, TypeError, ImportError) as exc:
        logger.error("Trip preview: plan failed: %s", exc)
        return _fail(f"Trip plan failed: {exc}")

    _emit({
        "kind": "preview",
        "planned_count": plan.planned_count,
        "matched_count": plan.selected_count,
        "skipped_count": plan.skipped_count,
        "entries": [
            {
                "source_path": str(e.source_path),
                "target_path": str(e.target_path) if e.target_path else None,
                "status": e.status,
                "size_bytes": e.scanned_file.size_bytes,
            }
            for e in plan.entries[:200]
        ],
    })
    return 0


def cmd_apply() -> int:
    """Execute trip collection plan from stdin JSON options (copies/links files)."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    try:
        options = _parse_options(payload)
    except (TypeError, ValueError, KeyError) as exc:
        logger.error("Trip apply: invalid options: %s", exc)
        return _fail(f"Invalid options: {exc}")

    try:
        plan = build_trip_dry_run(options)
        logger.info("Starting trip apply execution: %s", options.label)
        result = execute_trip_plan(plan, apply=True)
    except (OSError, ValueError, RuntimeError, TypeError, ImportError) as exc:
        logger.error("Trip apply: execution failed: %s", exc)
        return _fail(f"Trip execution failed: {exc}")

    _emit({
        "kind": "apply",
        "executed_count": result.executed_count,
        "linked_count": result.linked_count,
        "copied_count": result.copied_count,
        "skipped_count": result.skipped_count,
    })
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media_manager.bridge_trip")
    parser.add_argument("action", choices=["preview", "apply"])
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv or sys.argv[1:])
    return cmd_preview() if args.action == "preview" else cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
