from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from media_manager.core.gui_review_workbench_table_model import build_review_workbench_table_model
from media_manager.core.gui_review_workbench_view_models import (
    build_ui_review_workbench_view_model,
)

REVIEW_WORKBENCH_CONTROLLER_STATE_KIND = "ui_review_workbench_controller_state"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def build_review_workbench_view_state(
    *,
    duplicate_review: Mapping[str, Any],
    similar_images: Mapping[str, Any],
    decision_summary: Mapping[str, Any],
    people_review_summary: Mapping[str, Any] | None = None,
    selected_lane_id: str | None = None,
    lane_status_filter: str = "all",
    lane_query: str = "",
    lane_sort_mode: str = "attention_first",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    view_model = build_ui_review_workbench_view_model(
        duplicate_review=duplicate_review,
        similar_images=similar_images,
        decision_summary=decision_summary,
        people_review_summary=people_review_summary,
        selected_lane_id=selected_lane_id,
        lane_status_filter=lane_status_filter,
        lane_query=lane_query,
        lane_sort_mode=lane_sort_mode,
    )
    lanes = list(view_model["sorted_filtered_lanes"])  # type: ignore[index]
    table_model = build_review_workbench_table_model(
        lanes,
        selected_lane_id=str(view_model.get("selected_lane_id") or "") or None,
        page=page,
        page_size=page_size,
    )
    return {
        "kind": REVIEW_WORKBENCH_CONTROLLER_STATE_KIND,
        "view_model": view_model,
        "table_model": table_model,
        "state": {
            "selected_lane_id": view_model.get("selected_lane_id"),
            "lane_status_filter": str(_as_mapping(view_model.get("lane_filter")).get("status") or "all"),
            "lane_query": str(_as_mapping(view_model.get("lane_filter")).get("query") or ""),
            "lane_sort_mode": str(_as_mapping(view_model.get("lane_sort")).get("mode") or "attention_first"),
            "page": _as_int(_as_mapping(table_model.get("pagination")).get("page"), 1),
            "page_size": _as_int(_as_mapping(table_model.get("pagination")).get("page_size"), 20),
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
        },
    }


def build_review_workbench_update_intent(
    action: str,
    *,
    lane_id: str | None = None,
    status: str | None = None,
    query: str | None = None,
    sort_mode: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> dict[str, object]:
    normalized_action = str(action or "").strip().lower().replace("-", "_")
    allowed = {
        "select_lane",
        "set_filter",
        "set_query",
        "set_sort",
        "set_page",
        "set_page_size",
        "reset_view",
        "refresh_view",
        "open_selected_lane",
        "disabled_apply",
    }
    if normalized_action not in allowed:
        normalized_action = "noop"
    return {
        "kind": "ui_review_workbench_update_intent",
        "action": normalized_action,
        "lane_id": str(lane_id or "").strip() or None,
        "status": str(status or "").strip() or None,
        "query": str(query or "").strip(),
        "sort_mode": str(sort_mode or "").strip() or None,
        "page": page,
        "page_size": page_size,
        "executes_immediately": False,
        "executes_commands": False,
    }


def reduce_review_workbench_state(
    state: Mapping[str, Any],
    intent: Mapping[str, Any],
) -> dict[str, object]:
    current = _as_mapping(state)
    action = str(intent.get("action") or "noop")
    next_state = {
        "selected_lane_id": current.get("selected_lane_id"),
        "lane_status_filter": str(current.get("lane_status_filter") or "all"),
        "lane_query": str(current.get("lane_query") or ""),
        "lane_sort_mode": str(current.get("lane_sort_mode") or "attention_first"),
        "page": _as_int(current.get("page"), 1),
        "page_size": _as_int(current.get("page_size"), 20),
    }
    if action == "select_lane":
        next_state["selected_lane_id"] = intent.get("lane_id")
    elif action == "set_filter":
        next_state["lane_status_filter"] = str(intent.get("status") or "all")
        next_state["page"] = 1
    elif action == "set_query":
        next_state["lane_query"] = str(intent.get("query") or "")
        next_state["page"] = 1
    elif action == "set_sort":
        next_state["lane_sort_mode"] = str(intent.get("sort_mode") or "attention_first")
        next_state["page"] = 1
    elif action == "set_page":
        next_state["page"] = max(1, _as_int(intent.get("page"), _as_int(next_state["page"], 1)))
    elif action == "set_page_size":
        next_state["page_size"] = max(1, _as_int(intent.get("page_size"), _as_int(next_state["page_size"], 20)))
        next_state["page"] = 1
    elif action == "reset_view":
        next_state = {
            "selected_lane_id": None,
            "lane_status_filter": "all",
            "lane_query": "",
            "lane_sort_mode": "attention_first",
            "page": 1,
            "page_size": _as_int(current.get("page_size"), 20),
        }
    elif action in {"refresh_view", "open_selected_lane", "disabled_apply"}:
        # These are real UI events, but they are not state reducers here.
        # The desktop shell handles refresh/route/disabled-apply semantics.
        pass
    return {
        "kind": "ui_review_workbench_reduced_state",
        "state": next_state,
        "changed": next_state != dict(current),
        "executes_commands": False,
    }


__all__ = [
    "REVIEW_WORKBENCH_CONTROLLER_STATE_KIND",
    "build_review_workbench_update_intent",
    "build_review_workbench_view_state",
    "reduce_review_workbench_state",
]
