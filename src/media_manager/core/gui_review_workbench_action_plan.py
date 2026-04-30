from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_WORKBENCH_ACTION_PLAN_KIND = "ui_review_workbench_action_plan"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_review_workbench_action_plan(view_model: Mapping[str, Any]) -> dict[str, object]:
    selected_lane_id = str(view_model.get("selected_lane_id") or "")
    navigation_target = view_model.get("navigation_target_page_id")
    lane_filter = _as_mapping(view_model.get("lane_filter"))
    lane_sort = _as_mapping(view_model.get("lane_sort"))
    has_filter = str(lane_filter.get("status") or "all") != "all" or bool(str(lane_filter.get("query") or ""))
    actions = [
        {
            "id": "open-selected-lane",
            "label": "Open selected lane" if selected_lane_id else "Select a lane first",
            "enabled": bool(selected_lane_id and navigation_target),
            "lane_id": selected_lane_id or None,
            "page_id": navigation_target or None,
            "executes_immediately": False,
        },
        {
            "id": "reset-review-filters",
            "label": "Reset filters",
            "enabled": has_filter or str(lane_sort.get("mode") or "attention_first") != "attention_first",
            "page_id": "review-workbench",
            "executes_immediately": False,
        },
        {
            "id": "refresh-review-workbench",
            "label": "Refresh workbench",
            "enabled": True,
            "page_id": "review-workbench",
            "executes_immediately": False,
        },
        {
            "id": "apply-reviewed-decisions",
            "label": "Apply reviewed decisions",
            "enabled": False,
            "page_id": navigation_target or None,
            "executes_immediately": False,
            "requires_explicit_user_confirmation": True,
            "disabled_reason": "Apply remains disabled until a reviewed decision plan is present.",
        },
    ]
    return {
        "kind": REVIEW_WORKBENCH_ACTION_PLAN_KIND,
        "selected_lane_id": selected_lane_id or None,
        "action_count": len(actions),
        "enabled_action_count": sum(1 for action in actions if action["enabled"]),
        "actions": actions,
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
            "apply_enabled": False,
        },
    }


def find_review_workbench_action(action_plan: Mapping[str, Any], action_id: str) -> dict[str, object] | None:
    wanted = str(action_id or "")
    for action in action_plan.get("actions", []):
        if isinstance(action, Mapping) and str(action.get("id") or "") == wanted:
            return dict(action)
    return None


__all__ = [
    "REVIEW_WORKBENCH_ACTION_PLAN_KIND",
    "build_review_workbench_action_plan",
    "find_review_workbench_action",
]
