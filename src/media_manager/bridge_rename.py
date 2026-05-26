"""Rename bridge for the Tauri desktop app."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from media_manager.bridge_base import emit as _emit, fail as _fail
from media_manager.core.renamer import (
    RenamePlannerOptions,
    build_rename_dry_run,
    execute_rename_dry_run,
)

logger = logging.getLogger(__name__)


def _parse_options(payload: dict) -> RenamePlannerOptions:
    source_dirs_raw = payload.get("source_dirs") or [payload.get("source_dir", "")]
    source_dirs_raw = [p for p in source_dirs_raw if p]
    if not source_dirs_raw:
        raise ValueError("source_dir is required")

    source_dirs = tuple(Path(p) for p in source_dirs_raw)
    for d in source_dirs:
        if not d.is_dir():
            raise ValueError(f"source_dir does not exist or is not a directory: {d}")

    return RenamePlannerOptions(
        source_dirs=source_dirs,
        template=payload.get("template") or payload.get("pattern", "{date:%Y-%m-%d}_{stem}"),
        recursive=payload.get("recursive", True),
        include_hidden=payload.get("include_hidden", False),
        follow_symlinks=payload.get("follow_symlinks", False),
        include_associated_files=payload.get("include_associated_files", False),
        include_patterns=tuple(payload.get("include_patterns", ())),
        exclude_patterns=tuple(payload.get("exclude_patterns", ())),
        conflict_policy=payload.get("conflict_policy", "conflict"),
        date_source=payload.get("date_source", "auto"),
    )


def cmd_preview() -> int:
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
        logger.error("Rename preview: invalid options: %s", exc)
        return _fail(f"Invalid options: {exc}")

    try:
        dry_run = build_rename_dry_run(options)
    except Exception as exc:
        logger.exception("Rename preview: plan build failed")
        return _fail(f"Preview failed: {exc}")

    entries = [{
        "source_path": str(e.source_path),
        "target_path": str(e.target_path) if e.target_path else None,
        "status": e.status,
        "reason": e.reason or "",
    } for e in dry_run.entries]

    _emit({
        "kind": "rename_preview",
        "planned_count": dry_run.planned_count,
        "skipped_count": dry_run.skipped_count,
        "conflict_count": dry_run.conflict_count,
        "error_count": dry_run.error_count,
        "entries": entries,
    })
    return 0


def cmd_apply() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON: {exc}")

    try:
        options = _parse_options(payload)
    except (TypeError, ValueError, KeyError) as exc:
        logger.error("Rename apply: invalid options: %s", exc)
        return _fail(f"Invalid options: {exc}")

    try:
        dry_run = build_rename_dry_run(options)
        result = execute_rename_dry_run(dry_run, apply=True)
    except Exception as exc:
        logger.exception("Rename apply: execution failed")
        return _fail(f"Apply failed: {exc}")

    _emit({
        "kind": "rename_apply",
        "planned_count": dry_run.planned_count,
        "renamed_count": result.renamed_count,
        "skipped_count": result.skipped_count,
        "error_count": result.error_count,
        "conflict_count": result.conflict_count,
    })
    return 0


ACTIONS = {"preview": cmd_preview, "apply": cmd_apply}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="media_manager.bridge_rename")
    parser.add_argument("action", choices=list(ACTIONS.keys()))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv or sys.argv[1:])
    return ACTIONS[args.action]()


if __name__ == "__main__":
    raise SystemExit(main())
