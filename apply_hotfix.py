from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path.cwd()

DUPLICATES_PATH = REPO_ROOT / "src" / "media_manager" / "cli_duplicates.py"
INSPECT_PATH = REPO_ROOT / "src" / "media_manager" / "cli_inspect.py"

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Expected snippet not found for {label}.")
    return text.replace(old, new, 1)

def patch_cli_duplicates() -> None:
    text = DUPLICATES_PATH.read_text(encoding="utf-8")

    old_cleanup = '''        "cleanup_plan": {
            "total_groups": bundle.cleanup_plan.total_groups,
            "resolved_groups": bundle.cleanup_plan.resolved_groups,
            "unresolved_groups": bundle.cleanup_plan.unresolved_groups,
            "planned_removals": len(bundle.cleanup_plan.planned_removals),
            "estimated_reclaimable_bytes": bundle.cleanup_plan.estimated_reclaimable_bytes,
            "unresolved": [
                {
                    "group_id": item.group_id,
                    "file_size": item.file_size,
                    "candidate_count": len(item.candidate_paths),
                    "candidate_paths": [str(path) for path in item.candidate_paths],
                }
                for item in bundle.cleanup_plan.unresolved
            ],
        },'''
    new_cleanup = '''        "cleanup_plan": {
            "total_groups": getattr(bundle.cleanup_plan, "total_groups", len(result.exact_groups)),
            "resolved_groups": getattr(bundle.cleanup_plan, "resolved_groups", 0),
            "unresolved_groups": getattr(bundle.cleanup_plan, "unresolved_groups", 0),
            "planned_removals": len(getattr(bundle.cleanup_plan, "planned_removals", [])),
            "estimated_reclaimable_bytes": getattr(bundle.cleanup_plan, "estimated_reclaimable_bytes", 0),
            "unresolved": [
                {
                    "group_id": item.group_id,
                    "file_size": item.file_size,
                    "candidate_count": len(item.candidate_paths),
                    "candidate_paths": [str(path) for path in item.candidate_paths],
                }
                for item in getattr(bundle.cleanup_plan, "unresolved", [])
            ],
        },'''
    text = replace_once(text, old_cleanup, new_cleanup, "cli_duplicates cleanup_plan")

    old_dry_run = '''        "dry_run": {
            "ready": bundle.dry_run.ready,
            "planned_count": bundle.dry_run.planned_count,
            "blocked_count": bundle.dry_run.blocked_count,
            "delete_count": bundle.dry_run.delete_count,
            "exclude_from_copy_count": bundle.dry_run.exclude_from_copy_count,
            "exclude_from_move_count": bundle.dry_run.exclude_from_move_count,
            "rows": [
                {
                    "action_type": row.action_type,
                    "group_id": row.group_id,
                    "operation_mode": row.operation_mode,
                    "source_path": str(row.source_path),
                    "survivor_path": str(row.survivor_path) if row.survivor_path else None,
                    "target_path": str(row.target_path) if row.target_path else None,
                    "file_size": row.file_size,
                    "reason": row.reason,
                    "status": row.status,
                }
                for row in [*bundle.dry_run.planned_actions, *bundle.dry_run.blocked_actions]
            ],
        },'''
    new_dry_run = '''        "dry_run": {
            "ready": getattr(bundle.dry_run, "ready", False),
            "planned_count": getattr(bundle.dry_run, "planned_count", 0),
            "blocked_count": getattr(bundle.dry_run, "blocked_count", 0),
            "delete_count": getattr(bundle.dry_run, "delete_count", 0),
            "exclude_from_copy_count": getattr(bundle.dry_run, "exclude_from_copy_count", 0),
            "exclude_from_move_count": getattr(bundle.dry_run, "exclude_from_move_count", 0),
            "rows": [
                {
                    "action_type": row.action_type,
                    "group_id": row.group_id,
                    "operation_mode": row.operation_mode,
                    "source_path": str(row.source_path),
                    "survivor_path": str(row.survivor_path) if row.survivor_path else None,
                    "target_path": str(row.target_path) if row.target_path else None,
                    "file_size": row.file_size,
                    "reason": row.reason,
                    "status": row.status,
                }
                for row in [*getattr(bundle.dry_run, "planned_actions", []), *getattr(bundle.dry_run, "blocked_actions", [])]
            ],
        },'''
    text = replace_once(text, old_dry_run, new_dry_run, "cli_duplicates dry_run")

    old_preview = '''        "execution_preview": {
            "ready": bundle.execution_preview.ready,
            "executable_count": bundle.execution_preview.executable_count,
            "deferred_count": bundle.execution_preview.deferred_count,
            "blocked_count": bundle.execution_preview.blocked_count,
            "delete_count": bundle.execution_preview.delete_count,
            "reason_summary": _execution_preview_reason_summary(bundle.execution_preview),
            "rows": [
                {
                    "row_type": row.row_type,
                    "status": row.status,
                    "group_id": row.group_id,
                    "operation_mode": row.operation_mode,
                    "source_path": str(row.source_path),
                    "survivor_path": str(row.survivor_path) if row.survivor_path else None,
                    "target_path": str(row.target_path) if row.target_path else None,
                    "file_size": row.file_size,
                    "reason": row.reason,
                }
                for row in bundle.execution_preview.rows
            ],
        },'''
    new_preview = '''        "execution_preview": {
            "ready": getattr(bundle.execution_preview, "ready", False),
            "executable_count": getattr(bundle.execution_preview, "executable_count", 0),
            "deferred_count": getattr(bundle.execution_preview, "deferred_count", 0),
            "blocked_count": getattr(bundle.execution_preview, "blocked_count", 0),
            "delete_count": getattr(bundle.execution_preview, "delete_count", 0),
            "reason_summary": _execution_preview_reason_summary(bundle.execution_preview),
            "rows": [
                {
                    "row_type": row.row_type,
                    "status": row.status,
                    "group_id": row.group_id,
                    "operation_mode": row.operation_mode,
                    "source_path": str(row.source_path),
                    "survivor_path": str(row.survivor_path) if row.survivor_path else None,
                    "target_path": str(row.target_path) if row.target_path else None,
                    "file_size": row.file_size,
                    "reason": row.reason,
                }
                for row in getattr(bundle.execution_preview, "rows", [])
            ],
        },'''
    text = replace_once(text, old_preview, new_preview, "cli_duplicates execution_preview")

    DUPLICATES_PATH.write_text(text, encoding="utf-8")

def patch_cli_inspect() -> None:
    text = INSPECT_PATH.read_text(encoding="utf-8")

    old = '''    _print_summary_block("\nTimezone summary", summary["timezone_status_summary"])
    _print_summary_block("\nDecision policies", summary["decision_policy_summary"])
    _print_summary_block("\nMetadata error kinds", summary["metadata_error_kind_summary"])'''
    new = '''    _print_summary_block("\nTimezone summary", summary["timezone_status_summary"])
    if summary["decision_policy_summary"]:
        compact_policy_summary = ", ".join(f"{key}={value}" for key, value in summary["decision_policy_summary"].items())
        print(f"\nDecision policies: {compact_policy_summary}")
    _print_summary_block("\nDecision policies", summary["decision_policy_summary"])
    _print_summary_block("\nMetadata error kinds", summary["metadata_error_kind_summary"])'''
    text = replace_once(text, old, new, "cli_inspect decision policy summary")

    INSPECT_PATH.write_text(text, encoding="utf-8")

def main() -> int:
    if not DUPLICATES_PATH.exists():
        raise RuntimeError(f"Missing file: {DUPLICATES_PATH}")
    if not INSPECT_PATH.exists():
        raise RuntimeError(f"Missing file: {INSPECT_PATH}")

    patch_cli_duplicates()
    patch_cli_inspect()
    print("Patched:")
    print(f" - {DUPLICATES_PATH}")
    print(f" - {INSPECT_PATH}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
