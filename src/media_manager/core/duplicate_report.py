from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _path_or_none(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _sorted_counter(values: Iterable[object]) -> dict[str, int]:
    counter: Counter[str] = Counter(str(item) for item in values if item is not None)
    return dict(sorted(counter.items()))


def _scan_media_summary(scan_result) -> dict[str, object]:
    return {
        "extension_summary": dict(sorted(getattr(scan_result, "extension_summary", {}).items())),
        "media_kind_summary": dict(sorted(getattr(scan_result, "media_kind_summary", {}).items())),
        "image_file_count": _safe_int(getattr(scan_result, "image_file_count", 0)),
        "raw_image_file_count": _safe_int(getattr(scan_result, "raw_image_file_count", 0)),
        "video_file_count": _safe_int(getattr(scan_result, "video_file_count", 0)),
        "audio_file_count": _safe_int(getattr(scan_result, "audio_file_count", 0)),
        "unknown_media_kind_count": _safe_int(getattr(scan_result, "unknown_media_kind_count", 0)),
    }


def build_duplicate_summary(scan_result, bundle, execution_result=None) -> dict[str, object]:
    cleanup_plan = getattr(bundle, "cleanup_plan", None)
    dry_run = getattr(bundle, "dry_run", None)
    execution_preview = getattr(bundle, "execution_preview", None)

    exact_group_count = len(getattr(scan_result, "exact_groups", ()) or ())
    duplicate_file_count = _safe_int(getattr(scan_result, "exact_duplicate_files", 0))
    extra_duplicate_count = _safe_int(getattr(scan_result, "exact_duplicates", 0))
    unresolved_group_count = _safe_int(getattr(cleanup_plan, "unresolved_groups", 0))
    resolved_group_count = _safe_int(getattr(cleanup_plan, "resolved_groups", 0))
    planned_removal_count = len(getattr(cleanup_plan, "planned_removals", ()) or ())
    reclaimable_bytes = _safe_int(getattr(cleanup_plan, "estimated_reclaimable_bytes", 0))
    executable_delete_count = _safe_int(getattr(execution_preview, "delete_count", 0))
    blocked_count = _safe_int(getattr(dry_run, "blocked_count", 0))
    deferred_count = _safe_int(getattr(execution_preview, "deferred_count", 0))
    error_count = _safe_int(getattr(scan_result, "errors", 0))

    execution = None
    if execution_result is not None:
        execution = {
            "processed_rows": _safe_int(getattr(execution_result, "processed_rows", 0)),
            "executed_rows": _safe_int(getattr(execution_result, "executed_rows", 0)),
            "deleted_rows": _safe_int(getattr(execution_result, "deleted_rows", 0)),
            "blocked_rows": _safe_int(getattr(execution_result, "blocked_rows", 0)),
            "error_rows": _safe_int(getattr(execution_result, "error_rows", 0)),
        }

    return {
        "scanned_files": _safe_int(getattr(scan_result, "scanned_files", 0)),
        **_scan_media_summary(scan_result),
        "exact_group_count": exact_group_count,
        "duplicate_file_count": duplicate_file_count,
        "extra_duplicate_count": extra_duplicate_count,
        "resolved_group_count": resolved_group_count,
        "unresolved_group_count": unresolved_group_count,
        "planned_removal_count": planned_removal_count,
        "estimated_reclaimable_bytes": reclaimable_bytes,
        "executable_delete_count": executable_delete_count,
        "deferred_count": deferred_count,
        "blocked_count": blocked_count,
        "error_count": error_count,
        "execution": execution,
    }


def build_duplicate_outcome_report(
    *,
    scan_result,
    bundle,
    execution_result=None,
    apply_requested: bool = False,
    mode: str = "copy",
    policy: str | None = None,
) -> dict[str, object]:
    summary = build_duplicate_summary(scan_result, bundle, execution_result)
    exact_group_count = _safe_int(summary["exact_group_count"])
    unresolved_group_count = _safe_int(summary["unresolved_group_count"])
    planned_removal_count = _safe_int(summary["planned_removal_count"])
    executable_delete_count = _safe_int(summary["executable_delete_count"])
    deferred_count = _safe_int(summary["deferred_count"])
    blocked_count = _safe_int(summary["blocked_count"])
    error_count = _safe_int(summary["error_count"])

    execution_error_count = 0
    execution_deleted_count = 0
    if execution_result is not None:
        execution_error_count = _safe_int(getattr(execution_result, "error_rows", 0))
        execution_deleted_count = _safe_int(getattr(execution_result, "deleted_rows", 0))

    if error_count > 0 or execution_error_count > 0:
        status = "blocked"
        next_action = "Review duplicate scan or execution errors before continuing."
    elif unresolved_group_count > 0:
        status = "review_required"
        next_action = "Choose a keep file for each unresolved exact duplicate group or rerun with --policy."
    elif blocked_count > 0:
        status = "review_required"
        next_action = "Review blocked duplicate rows before applying destructive actions."
    elif apply_requested and execution_deleted_count > 0:
        status = "completed"
        next_action = "Review the execution journal and keep it with the run artifacts."
    elif apply_requested:
        status = "nothing_applied"
        next_action = "No duplicate rows were deleted. Review the report for blocked or deferred rows."
    elif mode == "delete" and executable_delete_count > 0:
        status = "delete_preview_ready"
        next_action = "Review the duplicate report and rerun with --apply --yes only if the delete plan is correct."
    elif planned_removal_count > 0 or deferred_count > 0:
        status = "plan_ready"
        next_action = "Use the report with cleanup/organize workflows; copy/move duplicate handling is currently deferred."
    elif exact_group_count > 0:
        status = "review_recommended"
        next_action = "Exact duplicate groups were found; choose a policy or session before planning cleanup."
    else:
        status = "nothing_found"
        next_action = "No exact duplicate groups were found."

    return {
        "command": "duplicates",
        "phase": "execution" if apply_requested else "plan",
        "status": status,
        "mode": mode,
        "policy": policy,
        "safe_to_apply": status == "delete_preview_ready",
        "needs_review": status in {"blocked", "review_required", "review_recommended", "delete_preview_ready"},
        "summary": summary,
        "counts": {
            "exact_group": exact_group_count,
            "unresolved_group": unresolved_group_count,
            "planned_removal": planned_removal_count,
            "executable_delete": executable_delete_count,
            "deferred": deferred_count,
            "blocked": blocked_count,
            "error": error_count + execution_error_count,
        },
        "next_action": next_action,
    }


def _group_quality(group) -> str:
    if bool(getattr(group, "same_name", False)) and bool(getattr(group, "same_suffix", False)):
        return "same_name_same_suffix"
    if bool(getattr(group, "same_suffix", False)):
        return "same_suffix"
    return "mixed_names_or_suffixes"


def _group_media_reasons(group) -> list[str]:
    reasons: list[str] = []
    media_kind_summary = dict(getattr(group, "media_kind_summary", {}) or {})
    extension_summary = dict(getattr(group, "extension_summary", {}) or {})
    if len(media_kind_summary) > 1:
        reasons.append("mixed_media_kinds")
    if len(extension_summary) > 1:
        reasons.append("mixed_extensions")
    if media_kind_summary.get("video", 0) > 0:
        reasons.append("video_duplicate_group")
    if media_kind_summary.get("raw-image", 0) > 0:
        reasons.append("raw_image_duplicate_group")
    if media_kind_summary.get("audio", 0) > 0:
        reasons.append("audio_duplicate_group")
    return reasons


def build_duplicate_review_export(
    *,
    scan_result,
    bundle,
    decision_rows: list[dict[str, object]] | None = None,
    similar_review=None,
    candidate_limit: int = 50,
) -> dict[str, object]:
    cleanup_plan = getattr(bundle, "cleanup_plan", None)
    execution_preview = getattr(bundle, "execution_preview", None)
    exact_groups = list(getattr(scan_result, "exact_groups", ()) or ())
    decisions = dict(getattr(bundle, "decisions", {}) or {})
    decision_rows = list(decision_rows or [])
    decision_by_group_id = {str(row.get("group_id")): row for row in decision_rows if row.get("group_id") is not None}

    candidates: list[dict[str, object]] = []
    section_counter: Counter[str] = Counter()
    reason_counter: Counter[str] = Counter()

    for group in exact_groups:
        group_id = None
        for row in decision_rows:
            candidate_paths = set(str(path) for path in row.get("candidate_paths", []) or [])
            group_paths = set(str(path) for path in getattr(group, "files", []) or [])
            if group_paths and candidate_paths == group_paths:
                group_id = str(row.get("group_id"))
                break
        if group_id is None:
            # Fall back to a stable enough display id when called from tests with incomplete rows.
            group_id = f"{getattr(group, 'file_size', 0)}:{getattr(group, 'full_digest', '')}"

        decision_row = decision_by_group_id.get(group_id, {})
        reasons: list[str] = []
        if group_id not in decisions:
            reasons.append("missing_keep_decision")
        quality = _group_quality(group)
        if quality != "same_name_same_suffix":
            reasons.append(quality)
        if len(getattr(group, "files", []) or []) > 2:
            reasons.append("multi_file_group")
        reasons.extend(reason for reason in _group_media_reasons(group) if reason not in reasons)

        if reasons:
            section_counter["exact_duplicates"] += 1
            for reason in reasons:
                reason_counter[reason] += 1
            if len(candidates) < candidate_limit:
                candidates.append(
                    {
                        "section": "exact_duplicates",
                        "group_id": group_id,
                        "status": decision_row.get("status", "decided" if group_id in decisions else "unresolved"),
                        "review_reasons": reasons,
                        "file_size": _safe_int(getattr(group, "file_size", 0)),
                        "candidate_count": len(getattr(group, "files", []) or []),
                        "candidate_paths": [str(path) for path in getattr(group, "files", []) or []],
                        "keep_path": decision_row.get("keep_path", decisions.get(group_id)),
                        "same_name": bool(getattr(group, "same_name", False)),
                        "same_suffix": bool(getattr(group, "same_suffix", False)),
                        "extension_summary": dict(sorted(getattr(group, "extension_summary", {}).items())),
                        "media_kind_summary": dict(sorted(getattr(group, "media_kind_summary", {}).items())),
                    }
                )

    for row in getattr(execution_preview, "rows", []) or []:
        if getattr(row, "status", None) != "blocked":
            continue
        section_counter["execution_preview"] += 1
        reason = str(getattr(row, "reason", "blocked"))
        reason_counter[reason] += 1
        if len(candidates) < candidate_limit:
            candidates.append(
                {
                    "section": "execution_preview",
                    "group_id": str(getattr(row, "group_id", "")),
                    "status": "blocked",
                    "review_reasons": [reason],
                    "source_path": _path_or_none(getattr(row, "source_path", None)),
                    "survivor_path": _path_or_none(getattr(row, "survivor_path", None)),
                    "target_path": _path_or_none(getattr(row, "target_path", None)),
                    "file_size": _safe_int(getattr(row, "file_size", 0)),
                }
            )

    similar_candidate_count = 0
    if similar_review is not None:
        for row in getattr(similar_review, "rows", []) or []:
            if getattr(row, "status", None) != "review":
                continue
            similar_candidate_count += 1
            section_counter["similar_images"] += 1
            reason = str(getattr(row, "reason", "similar_image_review"))
            reason_counter[reason] += 1
            if len(candidates) < candidate_limit:
                candidates.append(
                    {
                        "section": "similar_images",
                        "group_index": _safe_int(getattr(row, "group_index", 0)),
                        "status": getattr(row, "status", None),
                        "review_reasons": [reason],
                        "source_path": _path_or_none(getattr(row, "path", None)),
                        "recommended_keep_path": _path_or_none(getattr(row, "recommended_keep_path", None)),
                        "distance_to_keep": _safe_int(getattr(row, "distance_to_keep", 0)),
                    }
                )

    candidate_count = sum(section_counter.values())
    return {
        "candidate_count": candidate_count,
        "candidate_limit": candidate_limit,
        "truncated": candidate_count > len(candidates),
        "section_summary": dict(sorted(section_counter.items())),
        "reason_summary": dict(sorted(reason_counter.items())),
        "exact_duplicate_group_count": len(exact_groups),
        "unresolved_exact_group_count": _safe_int(getattr(cleanup_plan, "unresolved_groups", 0)),
        "similar_review_candidate_count": similar_candidate_count,
        "media_kind_summary": dict(sorted(getattr(scan_result, "media_kind_summary", {}).items())),
        "extension_summary": dict(sorted(getattr(scan_result, "extension_summary", {}).items())),
        "candidates": candidates,
    }


__all__ = [
    "build_duplicate_outcome_report",
    "build_duplicate_review_export",
    "build_duplicate_summary",
]
