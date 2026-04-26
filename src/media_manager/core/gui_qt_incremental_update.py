from __future__ import annotations

from collections.abc import Mapping
from typing import Any

UPDATE_SCHEMA_VERSION = "1.0"

def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def build_incremental_update_plan(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, object]:
    changes: list[dict[str, object]] = []
    if previous.get("active_page_id") != current.get("active_page_id"):
        changes.append({"kind": "switch_page", "from": previous.get("active_page_id"), "to": current.get("active_page_id"), "requires_rebuild": True})
    prev_page = _mapping(previous.get("page"))
    cur_page = _mapping(current.get("page"))
    if prev_page.get("page_id") != cur_page.get("page_id"):
        changes.append({"kind": "replace_page_widget", "page_id": cur_page.get("page_id"), "requires_rebuild": True})
    elif prev_page != cur_page:
        changes.append({"kind": "refresh_page_content", "page_id": cur_page.get("page_id"), "requires_rebuild": False})
    if previous.get("theme") != current.get("theme"):
        changes.append({"kind": "apply_stylesheet", "requires_rebuild": False})
    if previous.get("navigation") != current.get("navigation"):
        changes.append({"kind": "refresh_navigation", "requires_rebuild": False})
    return {
        "schema_version": UPDATE_SCHEMA_VERSION,
        "kind": "qt_incremental_update_plan",
        "change_count": len(changes),
        "requires_full_rebuild": any(change.get("requires_rebuild") for change in changes),
        "changes": changes,
    }

def update_plan_summary(plan: Mapping[str, Any]) -> dict[str, object]:
    changes = plan.get("changes") if isinstance(plan.get("changes"), list) else []
    return {
        "change_count": len(changes),
        "requires_full_rebuild": bool(plan.get("requires_full_rebuild")),
        "kinds": sorted({str(item.get("kind")) for item in changes if isinstance(item, Mapping) and item.get("kind")}),
    }

__all__ = ["UPDATE_SCHEMA_VERSION", "build_incremental_update_plan", "update_plan_summary"]
