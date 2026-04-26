from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PEOPLE_REVIEW_TIMELINE_SCHEMA_VERSION = "1.0"

_STAGE_ORDER = ("scan", "bundle", "review", "apply_preview", "catalog_apply", "rescan")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _stage(stage_id: str, *, label: str, status: str, enabled: bool, description: str = "") -> dict[str, object]:
    return {
        "id": stage_id,
        "label": label,
        "status": status,
        "enabled": enabled,
        "description": description,
    }


def build_people_review_timeline(
    *,
    bundle_summary: Mapping[str, Any] | None = None,
    workspace_overview: Mapping[str, Any] | None = None,
    audit_preview: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    bundle = _as_mapping(bundle_summary)
    overview = _as_mapping(workspace_overview)
    audit = _as_mapping(audit_preview)
    ready_groups = _as_int(overview.get("ready_group_count"))
    group_count = _as_int(overview.get("group_count"))
    face_count = _as_int(overview.get("face_count"))
    has_bundle = bool(bundle.get("ready_for_gui") or bundle.get("manifest_path") or group_count or face_count)
    has_review_data = group_count > 0 or face_count > 0
    audit_summary = _as_mapping(audit.get("summary"))
    safe_to_apply = bool(audit.get("safe_to_apply") or audit_summary.get("safe_to_apply"))
    blocked_count = _as_int(audit_summary.get("blocked_group_count"))
    applied = bool(audit.get("applied") or audit.get("catalog_updated"))

    stages = [
        _stage("scan", label="Scan faces", status="complete" if has_bundle else "pending", enabled=True),
        _stage("bundle", label="Build review bundle", status="complete" if has_bundle else "pending", enabled=True),
        _stage("review", label="Review groups", status="complete" if ready_groups else "active" if has_review_data else "pending", enabled=has_bundle),
        _stage(
            "apply_preview",
            label="Preview catalog apply",
            status="blocked" if blocked_count else "complete" if safe_to_apply else "pending",
            enabled=ready_groups > 0,
        ),
        _stage("catalog_apply", label="Apply to catalog", status="complete" if applied else "ready" if safe_to_apply else "pending", enabled=safe_to_apply),
        _stage("rescan", label="Rescan to verify", status="pending", enabled=applied),
    ]
    next_stage = next((item["id"] for item in stages if item["status"] in {"active", "ready", "pending", "blocked"} and item["enabled"]), None)
    return {
        "schema_version": PEOPLE_REVIEW_TIMELINE_SCHEMA_VERSION,
        "kind": "people_review_timeline",
        "stage_order": list(_STAGE_ORDER),
        "group_count": group_count,
        "face_count": face_count,
        "ready_group_count": ready_groups,
        "safe_to_apply": safe_to_apply,
        "next_stage_id": next_stage,
        "stages": stages,
    }


__all__ = ["PEOPLE_REVIEW_TIMELINE_SCHEMA_VERSION", "build_people_review_timeline"]
