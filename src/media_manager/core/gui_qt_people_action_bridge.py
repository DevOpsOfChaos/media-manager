from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PEOPLE_ACTION_BRIDGE_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any, default: str = "") -> str:
    return str(value) if value is not None else default


def build_people_review_button_bar(page_model: Mapping[str, Any]) -> dict[str, Any]:
    editor = _as_mapping(page_model.get("editor"))
    selected_group_id = _text(editor.get("selected_group_id") or page_model.get("selected_group_id"))
    detail_actions = [item for item in _as_list(editor.get("detail_actions")) if isinstance(item, Mapping)]
    buttons = []
    for action in detail_actions:
        action_id = _text(action.get("id"))
        buttons.append(
            {
                "id": action_id,
                "label": action.get("label") or action_id.replace("_", " ").title(),
                "enabled": bool(selected_group_id) and bool(action.get("enabled", True)),
                "variant": action.get("variant", "secondary"),
                "risk_level": action.get("risk_level", "safe"),
                "requires_confirmation": action.get("risk_level") in {"high", "destructive"} or action.get("variant") == "danger",
                "selected_group_id": selected_group_id or None,
            }
        )
    return {
        "schema_version": PEOPLE_ACTION_BRIDGE_SCHEMA_VERSION,
        "kind": "people_review_button_bar",
        "selected_group_id": selected_group_id or None,
        "button_count": len(buttons),
        "enabled_button_count": sum(1 for item in buttons if item["enabled"]),
        "buttons": buttons,
    }


def people_button_to_session_intent(button: Mapping[str, Any]) -> dict[str, Any]:
    action_id = _text(button.get("id"))
    group_id = button.get("selected_group_id")
    mapping = {
        "accept_group": "group_set_apply",
        "rename_group": "group_rename_dialog",
        "split_wrong_faces": "group_split_dialog",
        "apply_ready_groups": "review_apply_preview",
    }
    return {
        "schema_version": PEOPLE_ACTION_BRIDGE_SCHEMA_VERSION,
        "kind": "people_review_session_intent",
        "action_id": action_id,
        "session_action": mapping.get(action_id, "unknown"),
        "group_id": group_id,
        "enabled": bool(button.get("enabled")),
        "requires_confirmation": bool(button.get("requires_confirmation")),
        "executes_immediately": False,
    }


__all__ = ["PEOPLE_ACTION_BRIDGE_SCHEMA_VERSION", "build_people_review_button_bar", "people_button_to_session_intent"]
