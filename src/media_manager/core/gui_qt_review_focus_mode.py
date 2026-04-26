from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_FOCUS_SCHEMA_VERSION = "1.0"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_review_focus_mode(page_model: Mapping[str, Any], *, selected_group_id: str | None = None, selected_face_id: str | None = None) -> dict[str, object]:
    groups = [_mapping(item) for item in _list(page_model.get("groups")) if isinstance(item, Mapping)]
    selected_group = None
    if selected_group_id:
        selected_group = next((group for group in groups if str(group.get("group_id")) == str(selected_group_id)), None)
    if selected_group is None and groups:
        selected_group = groups[0]
    face_refs = _list(_mapping(page_model.get("detail")).get("faces"))
    selected_face = None
    if selected_face_id:
        selected_face = next((_mapping(face) for face in face_refs if str(_mapping(face).get("face_id")) == str(selected_face_id)), None)
    if selected_face is None and face_refs:
        selected_face = _mapping(face_refs[0])
    return {
        "schema_version": REVIEW_FOCUS_SCHEMA_VERSION,
        "kind": "review_focus_mode",
        "enabled": bool(selected_group),
        "selected_group_id": selected_group.get("group_id") if selected_group else None,
        "selected_group_label": selected_group.get("display_label") if selected_group else None,
        "selected_face_id": selected_face.get("face_id") if selected_face else None,
        "face_count": len(face_refs),
        "side_panel": "face_detail" if selected_face else "group_summary" if selected_group else "empty",
        "privacy_notice_visible": bool(selected_group),
    }


def build_focus_toolbar(focus_mode: Mapping[str, Any]) -> dict[str, object]:
    enabled = bool(focus_mode.get("enabled"))
    actions = [
        {"id": "accept_group", "label": "Accept group", "enabled": enabled, "executes_immediately": False},
        {"id": "reject_face", "label": "Reject face", "enabled": enabled and bool(focus_mode.get("selected_face_id")), "executes_immediately": False},
        {"id": "split_selection", "label": "Split selection", "enabled": enabled and bool(focus_mode.get("selected_face_id")), "requires_confirmation": True, "executes_immediately": False},
    ]
    return {
        "schema_version": REVIEW_FOCUS_SCHEMA_VERSION,
        "kind": "focus_toolbar",
        "action_count": len(actions),
        "enabled_action_count": sum(1 for action in actions if action.get("enabled")),
        "actions": actions,
    }


__all__ = ["REVIEW_FOCUS_SCHEMA_VERSION", "build_focus_toolbar", "build_review_focus_mode"]
