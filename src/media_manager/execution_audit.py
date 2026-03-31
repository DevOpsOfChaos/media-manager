from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def determine_duplicate_cli_exit_code(
    scan_result,
    execution_result,
    *,
    apply_requested: bool,
) -> int:
    if execution_result is not None:
        if execution_result.error_rows > 0:
            return 2
        if apply_requested and (execution_result.blocked_rows > 0 or execution_result.deferred_rows > 0):
            return 3
    return 0 if scan_result.errors == 0 else 1


def classify_duplicate_execution_status(
    scan_result,
    execution_result,
    *,
    apply_requested: bool,
) -> str:
    if execution_result is None:
        return "planned_only" if scan_result.errors == 0 else "scan_errors"
    if execution_result.error_rows > 0:
        return "execution_errors"
    if apply_requested and (execution_result.blocked_rows > 0 or execution_result.deferred_rows > 0):
        return "apply_incomplete"
    if apply_requested:
        return "applied"
    return "preview_only"


def build_duplicate_execution_audit_payload(
    scan_result,
    bundle,
    execution_result,
    *,
    apply_requested: bool,
) -> dict[str, object]:
    recommended_exit_code = determine_duplicate_cli_exit_code(
        scan_result,
        execution_result,
        apply_requested=apply_requested,
    )
    execution_status = classify_duplicate_execution_status(
        scan_result,
        execution_result,
        apply_requested=apply_requested,
    )

    return {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "apply_requested": apply_requested,
        "execution_status": execution_status,
        "recommended_exit_code": recommended_exit_code,
        "operation_mode": bundle.dry_run.planned_actions[0].operation_mode if bundle.dry_run.planned_actions else (bundle.dry_run.blocked_actions[0].operation_mode if bundle.dry_run.blocked_actions else None),
        "scan": {
            "scanned_files": scan_result.scanned_files,
            "size_candidate_files": scan_result.size_candidate_files,
            "hashed_files": scan_result.hashed_files,
            "exact_groups": len(scan_result.exact_groups),
            "duplicate_files": scan_result.exact_duplicate_files,
            "extra_duplicates": scan_result.exact_duplicates,
            "errors": scan_result.errors,
        },
        "decisions_count": len(bundle.decisions),
        "cleanup_plan": {
            "total_groups": bundle.cleanup_plan.total_groups,
            "resolved_groups": bundle.cleanup_plan.resolved_groups,
            "unresolved_groups": bundle.cleanup_plan.unresolved_groups,
            "planned_removals": len(bundle.cleanup_plan.planned_removals),
            "estimated_reclaimable_bytes": bundle.cleanup_plan.estimated_reclaimable_bytes,
        },
        "dry_run": {
            "ready": bundle.dry_run.ready,
            "planned_count": bundle.dry_run.planned_count,
            "blocked_count": bundle.dry_run.blocked_count,
            "delete_count": bundle.dry_run.delete_count,
            "exclude_from_copy_count": bundle.dry_run.exclude_from_copy_count,
            "exclude_from_move_count": bundle.dry_run.exclude_from_move_count,
        },
        "execution_preview": {
            "ready": bundle.execution_preview.ready,
            "executable_count": bundle.execution_preview.executable_count,
            "deferred_count": bundle.execution_preview.deferred_count,
            "blocked_count": bundle.execution_preview.blocked_count,
            "delete_count": bundle.execution_preview.delete_count,
        },
        "execution_run": None
        if execution_result is None
        else {
            "processed_rows": execution_result.processed_rows,
            "executable_rows": execution_result.executable_rows,
            "executed_rows": execution_result.executed_rows,
            "deferred_rows": execution_result.deferred_rows,
            "blocked_rows": execution_result.blocked_rows,
            "error_rows": execution_result.error_rows,
            "entries": [
                {
                    "row_type": entry.row_type,
                    "status": entry.status,
                    "source_path": str(entry.source_path),
                    "survivor_path": str(entry.survivor_path) if entry.survivor_path else None,
                    "target_path": str(entry.target_path) if entry.target_path else None,
                    "outcome": entry.outcome,
                    "reason": entry.reason,
                }
                for entry in execution_result.entries
            ],
        },
    }


def write_duplicate_execution_audit_log(
    file_path: str | Path,
    scan_result,
    bundle,
    execution_result,
    *,
    apply_requested: bool,
) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_duplicate_execution_audit_payload(
        scan_result,
        bundle,
        execution_result,
        apply_requested=apply_requested,
    )
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
