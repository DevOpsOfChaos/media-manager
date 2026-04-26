from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_SESSION_PANEL_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_review_session_panel(page_model: Mapping[str, Any]) -> dict[str, object]:
    page_id = str(page_model.get("page_id") or "people-review")
    queue = _mapping(page_model.get("queue"))
    editor = _mapping(page_model.get("editor"))
    detail = _mapping(page_model.get("detail"))
    selected_group_id = page_model.get("selected_group_id") or editor.get("selected_group_id")
    groups = _list(queue.get("groups") or page_model.get("groups"))
    detail_actions = [dict(item) for item in _list(editor.get("detail_actions")) if isinstance(item, Mapping)]
    blocked = []
    if not groups:
        blocked.append("No people groups are loaded.")
    if not selected_group_id:
        blocked.append("No people group is selected.")
    return {
        "schema_version": REVIEW_SESSION_PANEL_SCHEMA_VERSION,
        "kind": "qt_review_session_panel",
        "page_id": page_id,
        "selected_group_id": selected_group_id,
        "group_count": int(queue.get("group_count") or len(groups)),
        "visible_group_count": len(groups),
        "face_count": len(_list(detail.get("faces"))),
        "action_count": len(detail_actions),
        "actions": [
            {
                "id": str(action.get("id") or "action"),
                "label": str(action.get("label") or action.get("id") or "Action"),
                "enabled": not blocked or str(action.get("id")) in {"refresh_people_review"},
                "requires_confirmation": bool(action.get("requires_confirmation") or action.get("risk_level") in {"high", "destructive"}),
                "executes_immediately": False,
            }
            for action in detail_actions
        ],
        "blocked_reasons": blocked,
        "ready_for_review": bool(groups and selected_group_id),
    }


def summarize_qt_review_session_panel(panel: Mapping[str, Any]) -> dict[str, object]:
    return {
        "schema_version": REVIEW_SESSION_PANEL_SCHEMA_VERSION,
        "kind": "qt_review_session_panel_summary",
        "ready_for_review": bool(panel.get("ready_for_review")),
        "group_count": int(panel.get("group_count") or 0),
        "face_count": int(panel.get("face_count") or 0),
        "blocked_count": len(_list(panel.get("blocked_reasons"))),
        "confirmation_count": sum(1 for item in _list(panel.get("actions")) if _mapping(item).get("requires_confirmation")),
    }


__all__ = ["REVIEW_SESSION_PANEL_SCHEMA_VERSION", "build_qt_review_session_panel", "summarize_qt_review_session_panel"]
