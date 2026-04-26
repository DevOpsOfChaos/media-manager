from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_LANE_SCHEMA_VERSION = "1.0"
_LANES = ["needs_name", "needs_review", "ready_to_apply", "done", "blocked"]


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _lane_for_group(group: Mapping[str, Any]) -> str:
    status = str(group.get("status") or "")
    if status in _LANES:
        return status
    if group.get("blocked_reason"):
        return "blocked"
    return "needs_review"


def build_review_lanes(groups: list[Mapping[str, Any]] | None = None) -> dict[str, object]:
    lanes = {lane: [] for lane in _LANES}
    for group in groups or []:
        lane = _lane_for_group(group)
        lanes[lane].append({
            "group_id": group.get("group_id"),
            "label": group.get("display_label") or group.get("group_id"),
            "face_count": group.get("face_count", 0),
            "status": group.get("status"),
        })
    return {
        "schema_version": REVIEW_LANE_SCHEMA_VERSION,
        "kind": "review_lanes",
        "lane_count": len(_LANES),
        "group_count": sum(len(items) for items in lanes.values()),
        "lanes": [{"id": lane, "title": lane.replace("_", " ").title(), "count": len(items), "items": items} for lane, items in lanes.items()],
    }


def build_review_lanes_from_page(page_model: Mapping[str, Any]) -> dict[str, object]:
    groups = [_mapping(item) for item in _list(page_model.get("groups")) if isinstance(item, Mapping)]
    return build_review_lanes(groups)


__all__ = ["REVIEW_LANE_SCHEMA_VERSION", "build_review_lanes", "build_review_lanes_from_page"]
