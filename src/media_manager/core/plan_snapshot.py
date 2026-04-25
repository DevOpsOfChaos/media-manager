from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = "1.0"
DEFAULT_ENTRY_LIMIT = 200


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _compact_path(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _entry_status(entry: Mapping[str, Any]) -> str | None:
    for key in ("status", "outcome", "action"):
        value = entry.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _entry_target(entry: Mapping[str, Any]) -> str | None:
    for key in ("target_path", "survivor_path", "keep_path"):
        value = _compact_path(entry.get(key))
        if value is not None:
            return value
    return None


def _entry_source(entry: Mapping[str, Any]) -> str | None:
    for key in ("source_path", "path", "file_path"):
        value = _compact_path(entry.get(key))
        if value is not None:
            return value
    files = _as_list(entry.get("files"))
    if files:
        return _compact_path(files[0])
    candidate_paths = _as_list(entry.get("candidate_paths"))
    if candidate_paths:
        return _compact_path(candidate_paths[0])
    return None


def _entry_kind(section: str, entry: Mapping[str, Any]) -> str:
    if section == "duplicates":
        if "candidate_paths" in entry or "files" in entry:
            return "duplicate_group"
        return "duplicate_row"
    if entry.get("group_id"):
        return "media_group"
    if entry.get("member_results"):
        return "group_execution"
    return "file"


def _review_reasons_for_entry(entry: Mapping[str, Any]) -> list[str]:
    reasons = entry.get("review_reasons")
    if isinstance(reasons, list):
        return [str(item) for item in reasons if item is not None]
    status = _entry_status(entry)
    derived: list[str] = []
    if status in {"conflict", "error", "blocked"}:
        derived.append(status)
    if _as_int(entry.get("association_warning_count")) > 0 or _as_list(entry.get("association_warnings")):
        derived.append("association_warning")
    return derived


def _compact_entry(section: str, entry: Mapping[str, Any], *, index: int) -> dict[str, Any]:
    candidate_paths = entry.get("candidate_paths")
    files = entry.get("files")
    member_results = entry.get("member_results")
    member_targets = entry.get("member_targets")

    row: dict[str, Any] = {
        "index": index,
        "section": section,
        "kind": _entry_kind(section, entry),
        "source_path": _entry_source(entry),
        "target_path": _entry_target(entry),
        "status": _entry_status(entry),
        "reason": entry.get("reason") if isinstance(entry.get("reason"), str) else None,
        "review_reasons": _review_reasons_for_entry(entry),
        "group_id": entry.get("group_id"),
        "group_kind": entry.get("group_kind"),
        "associated_file_count": _as_int(entry.get("associated_file_count")),
    }

    if isinstance(entry.get("rendered_name"), str):
        row["rendered_name"] = entry.get("rendered_name")
    if isinstance(entry.get("operation_mode"), str):
        row["operation_mode"] = entry.get("operation_mode")
    if isinstance(entry.get("action"), str):
        row["action"] = entry.get("action")
    if isinstance(candidate_paths, list):
        row["candidate_count"] = len(candidate_paths)
        row["candidate_paths_preview"] = [_compact_path(item) for item in candidate_paths[:8]]
    elif isinstance(files, list):
        row["candidate_count"] = len(files)
        row["candidate_paths_preview"] = [_compact_path(item) for item in files[:8]]
    if isinstance(member_results, list):
        row["member_result_count"] = len(member_results)
    if isinstance(member_targets, list):
        row["member_target_count"] = len(member_targets)
    if isinstance(entry.get("extension_summary"), dict):
        row["extension_summary"] = dict(sorted(entry["extension_summary"].items()))
    if isinstance(entry.get("media_kind_summary"), dict):
        row["media_kind_summary"] = dict(sorted(entry["media_kind_summary"].items()))
    return row


def _section_entries(report_payload: Mapping[str, Any], section: str) -> list[Mapping[str, Any]]:
    section_payload = _as_mapping(report_payload.get(section))
    candidates: list[Any] = []
    if section == "duplicates":
        for key in ("exact_groups", "groups", "decision_rows", "execution_preview_rows", "similar_groups"):
            values = section_payload.get(key)
            if isinstance(values, list):
                candidates.extend(values)
        for key in ("decision_rows", "exact_groups"):
            values = report_payload.get(key)
            if isinstance(values, list):
                candidates.extend(values)
        dry_run = _as_mapping(report_payload.get("dry_run"))
        values = dry_run.get("rows")
        if isinstance(values, list):
            candidates.extend(values)
        execution_preview = _as_mapping(report_payload.get("execution_preview"))
        values = execution_preview.get("rows")
        if isinstance(values, list):
            candidates.extend(values)
        similar_images = _as_mapping(report_payload.get("similar_images"))
        values = similar_images.get("groups")
        if isinstance(values, list):
            candidates.extend(values)
    else:
        values = section_payload.get("entries")
        if isinstance(values, list):
            candidates.extend(values)
    return [item for item in candidates if isinstance(item, Mapping)]


def _summarize_rows(rows: list[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    status_summary: dict[str, int] = {}
    kind_summary: dict[str, int] = {}
    section_summary: dict[str, int] = {}
    review_reason_summary: dict[str, int] = {}
    for row in rows:
        status = row.get("status")
        if isinstance(status, str) and status:
            status_summary[status] = status_summary.get(status, 0) + 1
        kind = row.get("kind")
        if isinstance(kind, str) and kind:
            kind_summary[kind] = kind_summary.get(kind, 0) + 1
        section = row.get("section")
        if isinstance(section, str) and section:
            section_summary[section] = section_summary.get(section, 0) + 1
        for reason in _as_list(row.get("review_reasons")):
            key = str(reason)
            review_reason_summary[key] = review_reason_summary.get(key, 0) + 1
    return {
        "status_summary": dict(sorted(status_summary.items())),
        "kind_summary": dict(sorted(kind_summary.items())),
        "section_summary": dict(sorted(section_summary.items())),
        "review_reason_summary": dict(sorted(review_reason_summary.items())),
    }


def build_plan_snapshot_from_report(
    *,
    command_name: str,
    report_payload: Mapping[str, Any],
    run_id: str | None = None,
    entry_limit: int = DEFAULT_ENTRY_LIMIT,
) -> dict[str, Any]:
    """Build a compact GUI-friendly snapshot of planned/reviewable rows from a full report."""
    max_entries = max(0, int(entry_limit))
    all_rows: list[dict[str, Any]] = []
    for section in ("organize", "rename", "duplicates", "cleanup", "execution"):
        for entry in _section_entries(report_payload, section):
            all_rows.append(_compact_entry(section, entry, index=len(all_rows) + 1))

    displayed_rows = all_rows[:max_entries]
    summary = _summarize_rows(displayed_rows)
    review = _as_mapping(report_payload.get("review"))
    outcome = _as_mapping(report_payload.get("outcome_report"))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _now_utc(),
        "command": command_name,
        "run_id": run_id,
        "entry_limit": max_entries,
        "entry_count": len(all_rows),
        "returned_entry_count": len(displayed_rows),
        "truncated": len(all_rows) > len(displayed_rows),
        "overview": {
            "status": outcome.get("status"),
            "safe_to_apply": outcome.get("safe_to_apply"),
            "needs_review": outcome.get("needs_review"),
            "next_action": outcome.get("next_action"),
            "review_candidate_count": _as_int(review.get("candidate_count")),
        },
        **summary,
        "entries": displayed_rows,
    }


__all__ = ["DEFAULT_ENTRY_LIMIT", "SCHEMA_VERSION", "build_plan_snapshot_from_report"]
