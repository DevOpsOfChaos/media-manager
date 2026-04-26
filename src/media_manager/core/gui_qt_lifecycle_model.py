from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LIFECYCLE_SCHEMA_VERSION = "1.0"

DEFAULT_STAGES = ("bootstrap", "load_settings", "build_model", "build_blueprint", "bind_signals", "show_window")

def build_qt_lifecycle_plan(*, has_settings: bool = False, has_people_bundle: bool = False, dry_run: bool = False) -> dict[str, object]:
    stages: list[dict[str, object]] = []
    for index, stage_id in enumerate(DEFAULT_STAGES, start=1):
        optional = stage_id == "load_settings" and not has_settings
        stages.append(
            {
                "index": index,
                "id": stage_id,
                "title": stage_id.replace("_", " ").title(),
                "optional": optional,
                "enabled": not optional,
                "status": "skipped" if optional else "pending",
            }
        )
    if has_people_bundle:
        stages.insert(
            4,
            {"index": 4, "id": "validate_people_bundle", "title": "Validate People Bundle", "optional": False, "enabled": True, "status": "pending"},
        )
        for idx, item in enumerate(stages, start=1):
            item["index"] = idx
    return {
        "schema_version": LIFECYCLE_SCHEMA_VERSION,
        "kind": "qt_lifecycle_plan",
        "dry_run": bool(dry_run),
        "stages": stages,
        "summary": {
            "stage_count": len(stages),
            "enabled_count": sum(1 for item in stages if item["enabled"]),
            "skipped_count": sum(1 for item in stages if item["status"] == "skipped"),
        },
    }

def mark_lifecycle_stage(plan: Mapping[str, Any], stage_id: str, status: str) -> dict[str, object]:
    updated = {**dict(plan)}
    stages = []
    for raw in plan.get("stages", []) if isinstance(plan.get("stages"), list) else []:
        item = dict(raw) if isinstance(raw, Mapping) else {}
        if item.get("id") == stage_id:
            item["status"] = str(status)
        stages.append(item)
    updated["stages"] = stages
    updated["summary"] = {
        "stage_count": len(stages),
        "done_count": sum(1 for item in stages if item.get("status") == "done"),
        "error_count": sum(1 for item in stages if item.get("status") == "error"),
        "pending_count": sum(1 for item in stages if item.get("status") == "pending"),
    }
    return updated

__all__ = ["LIFECYCLE_SCHEMA_VERSION", "build_qt_lifecycle_plan", "mark_lifecycle_stage"]
