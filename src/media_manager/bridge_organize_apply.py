"""Organize apply bridge for the Tauri desktop app.

Called by the Rust backend via subprocess.
Reads OrganizePlannerOptions JSON from stdin (same format as preview).
Rebuilds the dry-run plan, executes it, and returns the execution result.
Output: execution result JSON on stdout. Errors: JSON on stderr.

This bridge MODIFIES files (copies/moves according to the plan).
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from media_manager.core.leftover import remove_empty_directories
from media_manager.core.organizer import OrganizePlannerOptions, build_organize_dry_run, execute_organize_plan
from media_manager.core.outcome_report import build_execution_outcome_report


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _fail(message: str, exit_code: int = 1) -> int:
    print(json.dumps({"error": message}), file=sys.stderr)
    return exit_code


def _member_payload(member) -> dict:
    return {
        "source_path": str(member.source_path),
        "target_path": str(member.target_path) if member.target_path else None,
        "role": member.role,
        "is_main_file": member.is_main_file,
        "outcome": member.outcome,
        "reason": member.reason,
    }


def _build_journal_entries(execution_result) -> list[dict]:
    entries: list[dict] = []
    for item in execution_result.entries:
        for member in getattr(item, "member_results", ()):
            reversible = False
            undo_action = None
            undo_from = None
            undo_to = None
            if member.outcome == "copied":
                reversible = True
                undo_action = "delete_target"
                undo_from = str(member.target_path) if member.target_path else None
            elif member.outcome == "moved":
                reversible = True
                undo_action = "move_back"
                undo_from = str(member.target_path) if member.target_path else None
                undo_to = str(member.source_path)
            entries.append({
                "source_path": str(member.source_path),
                "target_path": str(member.target_path) if member.target_path else None,
                "outcome": member.outcome,
                "reason": member.reason,
                "reversible": reversible,
                "undo_action": undo_action,
                "undo_from_path": undo_from,
                "undo_to_path": undo_to,
                "group_id": getattr(item, "group_id", None),
                "group_kind": getattr(item, "group_kind", None),
                "role": member.role,
                "is_main_file": member.is_main_file,
            })
    return entries


def cmd_apply() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return _fail("Empty stdin. Expected JSON OrganizePlannerOptions.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _fail(f"Invalid JSON input: {exc}\nRaw input (first 500 chars): {raw[:500]}")

    try:
        source_dirs_raw = payload.get("source_dirs", [])
        if not source_dirs_raw:
            return _fail("source_dirs is required and must be non-empty.")
        target_root_raw = payload.get("target_root", "")
        if not target_root_raw:
            return _fail("target_root is required.")

        options = OrganizePlannerOptions(
            source_dirs=tuple(Path(p) for p in source_dirs_raw),
            target_root=Path(target_root_raw),
            pattern=payload.get("pattern", "{year}/{year_month_day}"),
            recursive=payload.get("recursive", True),
            include_hidden=payload.get("include_hidden", False),
            follow_symlinks=payload.get("follow_symlinks", False),
            operation_mode=payload.get("operation_mode", "copy"),
            include_associated_files=payload.get("include_associated_files", False),
            conflict_policy=payload.get("conflict_policy", "conflict"),
            include_patterns=tuple(payload.get("include_patterns", ())),
            exclude_patterns=tuple(payload.get("exclude_patterns", ())),
            batch_size=payload.get("batch_size", 0),
        )
    except (TypeError, ValueError) as exc:
        return _fail(f"Invalid options: {exc}\nPayload keys: {list(payload.keys())}\nTraceback:\n{traceback.format_exc()}")

    # Build plan
    try:
        plan = build_organize_dry_run(options)
    except Exception as exc:
        return _fail(f"Plan build failed: {exc}\nTraceback:\n{traceback.format_exc()}")

    if plan.planned_count == 0:
        return _fail("Nothing to execute — plan has no planned entries.", exit_code=0)

    # Execute
    try:
        result = execute_organize_plan(plan)
    except Exception as exc:
        return _fail(f"Execution failed: {exc}\nTraceback:\n{traceback.format_exc()}")

    # Cleanup empty directories if requested
    removed_dirs: list[str] = []
    if payload.get("cleanup_empty_dirs", False):
        for sd in options.source_dirs:
            try:
                dirs = remove_empty_directories(sd, "")
                removed_dirs.extend([str(d) for d in dirs])
            except Exception:
                pass

    # Build journal entries
    journal_entries = _build_journal_entries(result)

    # Outcome report
    outcome = build_execution_outcome_report(
        command_name="organize",
        apply_requested=True,
        processed_count=result.processed_count,
        executed_count=result.executed_count,
        skipped_count=result.skipped_count,
        conflict_count=result.conflict_count,
        error_count=result.error_count,
        status_summary=result.outcome_summary,
        reason_summary=result.reason_summary,
    )

    output: dict = {
        "kind": "apply",
        "dry_run": False,
        "options": {
            "source_dirs": [str(p) for p in options.source_dirs],
            "target_root": str(options.target_root),
            "pattern": options.pattern,
            "operation_mode": options.operation_mode,
            "include_associated_files": options.include_associated_files,
        },
        "executed_count": result.executed_count,
        "copied_count": result.copied_count,
        "moved_count": result.moved_count,
        "skipped_count": result.skipped_count,
        "conflict_count": result.conflict_count,
        "error_count": result.error_count,
        "outcome_summary": result.outcome_summary,
        "reason_summary": result.reason_summary,
        "removed_empty_dirs": removed_dirs,
        "removed_empty_dir_count": len(removed_dirs),
        "outcome_report": outcome,
        "entries": [
            {
                "source_path": str(item.source_path),
                "target_path": str(item.target_path) if item.target_path else None,
                "outcome": item.outcome,
                "reason": item.reason,
                "group_id": getattr(item, "group_id", None),
                "group_kind": getattr(item, "group_kind", getattr(item.plan_entry, "group_kind", "single")),
                "member_results": [_member_payload(m) for m in getattr(item, "member_results", ())],
            }
            for item in result.entries
        ],
        "journal_entries": journal_entries,
    }
    _emit(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="media_manager.bridge_organize_apply",
        description="Organize apply bridge for Tauri desktop app (executes copy/move).",
    )


def main(argv: list[str] | None = None) -> int:
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
