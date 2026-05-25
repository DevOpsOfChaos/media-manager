"""Duplicates apply bridge for the Tauri desktop app.

Reads scan config + decisions JSON from stdin.
Rebuilds the duplicate workflow bundle, executes decisions (delete/move/copy).
Output: execution result JSON on stdout. Errors: JSON on stderr.

THIS BRIDGE MODIFIES/DELETES FILES when apply=True.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from media_manager.duplicate_workflow import (
    DuplicateWorkflowBundle,
    build_duplicate_workflow_bundle,
    execute_duplicate_workflow_bundle,
)
from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def cmd_apply() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON with scan config and decisions.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}")

    source_dirs_raw = payload.get("source_dirs", [])
    if not source_dirs_raw:
        return _fail("source_dirs is required.")

    decisions = payload.get("decisions", {})
    if not decisions:
        return _fail("decisions is required and must be non-empty.")

    mode = payload.get("mode", "delete")
    policy = payload.get("policy", "first")
    target_root = payload.get("target_root", "")

    config = DuplicateScanConfig(
        source_dirs=[Path(p) for p in source_dirs_raw],
        include_patterns=tuple(payload.get("include_patterns", ())),
        exclude_patterns=tuple(payload.get("exclude_patterns", ())),
    )

    # Scan for duplicates
    try:
        scan_result = scan_exact_duplicates(config)
    except Exception as exc:
        return _fail(f"Duplicate scan failed: {exc}")

    # Build workflow bundle with decisions
    try:
        bundle = build_duplicate_workflow_bundle(
            scan_result.exact_groups,
            decisions=decisions,
            operation_mode=mode,
            target_root=Path(target_root) if target_root else None,
        )
    except Exception as exc:
        return _fail(f"Workflow build failed: {exc}")

    # Execute
    try:
        result = execute_duplicate_workflow_bundle(bundle, apply=True)
    except Exception as exc:
        return _fail(f"Execution failed: {exc}")

    # Build journal entries
    journal_entries: list[dict] = []
    for entry in result.entries:
        is_delete_action = entry.row_type == "filesystem_delete"
        reversible = entry.outcome in ("deleted", "moved") and is_delete_action
        journal_entries.append({
            "source_path": str(entry.source_path),
            "target_path": str(entry.target_path) if entry.target_path else None,
            "outcome": entry.outcome,
            "reason": entry.reason,
            "action": "delete" if entry.row_type == "filesystem_delete" else entry.row_type,
            "reversible": reversible,
            "undo_action": None,
            "undo_from_path": None,
            "undo_to_path": None,
        })

    output: dict = {
        "kind": "apply",
        "dry_run": False,
        "processed_rows": result.processed_rows,
        "executable_rows": result.executable_rows,
        "executed_rows": result.executed_rows,
        "deferred_rows": result.deferred_rows,
        "blocked_rows": result.blocked_rows,
        "error_rows": result.error_rows,
        "entries": [
            {
                "source_path": str(e.source_path),
                "target_path": str(e.target_path) if e.target_path else None,
                "outcome": e.outcome,
                "reason": e.reason,
                "action": "delete" if e.row_type == "filesystem_delete" else e.row_type,
            }
            for e in result.entries
        ],
        "journal_entries": journal_entries,
    }
    _emit(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="media_manager.bridge_duplicates_apply",
        description="Duplicates apply bridge for Tauri desktop app.",
    )


def main(argv: list[str] | None = None) -> int:
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
