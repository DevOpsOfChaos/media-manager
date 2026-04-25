from __future__ import annotations

from collections.abc import Mapping


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _sorted_int_mapping(values: Mapping[str, object] | None) -> dict[str, int]:
    if not values:
        return {}
    return {str(key): _safe_int(value) for key, value in sorted(values.items(), key=lambda item: str(item[0]))}


def build_plan_outcome_report(
    *,
    command_name: str,
    conflict_policy: str = "conflict",
    planned_count: int = 0,
    skipped_count: int = 0,
    conflict_count: int = 0,
    error_count: int = 0,
    missing_source_count: int = 0,
    review_candidate_count: int = 0,
    status_summary: Mapping[str, object] | None = None,
    reason_summary: Mapping[str, object] | None = None,
) -> dict[str, object]:
    planned_count = _safe_int(planned_count)
    skipped_count = _safe_int(skipped_count)
    conflict_count = _safe_int(conflict_count)
    error_count = _safe_int(error_count)
    missing_source_count = _safe_int(missing_source_count)
    review_candidate_count = _safe_int(review_candidate_count)
    actionable_count = planned_count
    blocked_count = conflict_count + error_count + missing_source_count
    total_count = planned_count + skipped_count + conflict_count + error_count

    if error_count > 0 or missing_source_count > 0:
        status = "blocked"
        next_action = "Resolve errors or missing sources before applying this plan."
    elif conflict_count > 0:
        status = "review_required"
        next_action = "Review conflicts or rerun with a different conflict policy."
    elif review_candidate_count > 0:
        status = "review_recommended"
        next_action = "Review candidates before applying the workflow."
    elif planned_count > 0:
        status = "ready"
        next_action = "Ready to apply when the plan matches expectations."
    elif skipped_count > 0:
        status = "nothing_to_do"
        next_action = "No planned actions remain; all entries were skipped."
    else:
        status = "empty"
        next_action = "No media actions were found for this command."

    return {
        "command": command_name,
        "phase": "plan",
        "status": status,
        "conflict_policy": conflict_policy,
        "safe_to_apply": status == "ready",
        "needs_review": status in {"blocked", "review_required", "review_recommended"},
        "total_count": total_count,
        "actionable_count": actionable_count,
        "blocked_count": blocked_count,
        "review_candidate_count": review_candidate_count,
        "counts": {
            "planned": planned_count,
            "skipped": skipped_count,
            "conflict": conflict_count,
            "error": error_count,
            "missing_source": missing_source_count,
        },
        "status_summary": _sorted_int_mapping(status_summary),
        "reason_summary": _sorted_int_mapping(reason_summary),
        "next_action": next_action,
    }


def build_execution_outcome_report(
    *,
    command_name: str,
    apply_requested: bool,
    processed_count: int = 0,
    executed_count: int = 0,
    preview_count: int = 0,
    skipped_count: int = 0,
    conflict_count: int = 0,
    error_count: int = 0,
    status_summary: Mapping[str, object] | None = None,
    action_summary: Mapping[str, object] | None = None,
    reason_summary: Mapping[str, object] | None = None,
) -> dict[str, object]:
    processed_count = _safe_int(processed_count)
    executed_count = _safe_int(executed_count)
    preview_count = _safe_int(preview_count)
    skipped_count = _safe_int(skipped_count)
    conflict_count = _safe_int(conflict_count)
    error_count = _safe_int(error_count)
    blocked_count = conflict_count + error_count

    if error_count > 0:
        status = "failed"
        next_action = "Review execution errors before running more operations."
    elif conflict_count > 0:
        status = "partial_review_required"
        next_action = "Review execution conflicts before rerunning."
    elif apply_requested and executed_count > 0:
        status = "completed"
        next_action = "Review the output and keep the journal for undo if needed."
    elif apply_requested:
        status = "nothing_applied"
        next_action = "No filesystem changes were applied."
    elif preview_count > 0:
        status = "preview_ready"
        next_action = "Preview is ready; rerun with apply when it matches expectations."
    else:
        status = "empty"
        next_action = "No executable entries were produced."

    return {
        "command": command_name,
        "phase": "execution" if apply_requested else "preview",
        "status": status,
        "apply_requested": bool(apply_requested),
        "needs_review": status in {"failed", "partial_review_required"},
        "processed_count": processed_count,
        "executed_count": executed_count,
        "preview_count": preview_count,
        "blocked_count": blocked_count,
        "counts": {
            "processed": processed_count,
            "executed": executed_count,
            "preview": preview_count,
            "skipped": skipped_count,
            "conflict": conflict_count,
            "error": error_count,
        },
        "status_summary": _sorted_int_mapping(status_summary),
        "action_summary": _sorted_int_mapping(action_summary),
        "reason_summary": _sorted_int_mapping(reason_summary),
        "next_action": next_action,
    }


def build_cleanup_outcome_report(
    *,
    conflict_policy: str = "conflict",
    missing_source_count: int = 0,
    duplicate_error_count: int = 0,
    duplicate_unresolved_groups: int = 0,
    organize_planned_count: int = 0,
    organize_skipped_count: int = 0,
    organize_conflict_count: int = 0,
    organize_error_count: int = 0,
    rename_planned_count: int = 0,
    rename_skipped_count: int = 0,
    rename_conflict_count: int = 0,
    rename_error_count: int = 0,
    review_candidate_count: int = 0,
    execution_status: str | None = None,
) -> dict[str, object]:
    missing_source_count = _safe_int(missing_source_count)
    duplicate_error_count = _safe_int(duplicate_error_count)
    duplicate_unresolved_groups = _safe_int(duplicate_unresolved_groups)
    review_candidate_count = _safe_int(review_candidate_count)

    organize = build_plan_outcome_report(
        command_name="cleanup.organize",
        conflict_policy=conflict_policy,
        planned_count=organize_planned_count,
        skipped_count=organize_skipped_count,
        conflict_count=organize_conflict_count,
        error_count=organize_error_count,
        missing_source_count=missing_source_count,
    )
    rename = build_plan_outcome_report(
        command_name="cleanup.rename",
        conflict_policy=conflict_policy,
        planned_count=rename_planned_count,
        skipped_count=rename_skipped_count,
        conflict_count=rename_conflict_count,
        error_count=rename_error_count,
        missing_source_count=missing_source_count,
    )
    duplicate_blocked_count = duplicate_error_count + duplicate_unresolved_groups
    hard_blocked_count = (
        missing_source_count
        + duplicate_error_count
        + organize_error_count
        + rename_error_count
    )
    review_blocked_count = duplicate_unresolved_groups + organize_conflict_count + rename_conflict_count

    if hard_blocked_count > 0:
        status = "blocked"
        next_action = "Resolve missing sources or errors before applying cleanup steps."
    elif review_blocked_count > 0:
        status = "review_required"
        next_action = "Review duplicate decisions and conflicts before applying cleanup steps."
    elif review_candidate_count > 0:
        status = "review_recommended"
        next_action = "Review candidates before applying cleanup steps."
    elif execution_status in {"failed", "partial_review_required"}:
        status = "execution_review_required"
        next_action = "Review the execution result before running more cleanup steps."
    elif execution_status in {"completed", "nothing_applied"}:
        status = execution_status
        next_action = "Review the execution output and journal."
    elif organize_planned_count or rename_planned_count:
        status = "ready"
        next_action = "Choose --apply-organize or --apply-rename when the plan matches expectations."
    else:
        status = "nothing_to_do"
        next_action = "No cleanup actions are currently planned."

    return {
        "command": "cleanup",
        "phase": "workflow",
        "status": status,
        "conflict_policy": conflict_policy,
        "safe_to_apply": status == "ready",
        "needs_review": status in {"blocked", "review_required", "review_recommended", "execution_review_required"},
        "review_candidate_count": review_candidate_count,
        "blocked_count": hard_blocked_count + review_blocked_count,
        "duplicate_blocked_count": duplicate_blocked_count,
        "sections": {
            "organize": organize,
            "rename": rename,
        },
        "counts": {
            "missing_source": missing_source_count,
            "duplicate_error": duplicate_error_count,
            "duplicate_unresolved_group": duplicate_unresolved_groups,
            "organize_planned": _safe_int(organize_planned_count),
            "rename_planned": _safe_int(rename_planned_count),
            "review_candidate": review_candidate_count,
        },
        "next_action": next_action,
    }
