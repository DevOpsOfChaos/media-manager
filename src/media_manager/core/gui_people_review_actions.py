from __future__ import annotations

from collections.abc import Mapping
from typing import Any

PEOPLE_REVIEW_ACTIONS_SCHEMA_VERSION = "1.0"


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _action(
    action_id: str,
    label: str,
    *,
    enabled: bool,
    category: str = "review",
    risk_level: str = "safe",
    blocked_reason: str | None = None,
    requires_confirmation: bool = False,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": action_id,
        "label": label,
        "category": category,
        "risk_level": risk_level,
        "enabled": bool(enabled),
        "requires_confirmation": bool(requires_confirmation),
    }
    if blocked_reason:
        payload["blocked_reason"] = blocked_reason
    return payload


def build_people_group_actions(group: Mapping[str, Any] | None = None) -> dict[str, object]:
    data = _as_mapping(group)
    status = _as_text(data.get("status")) or "needs_review"
    group_id = _as_text(data.get("group_id"))
    face_count = _as_int(data.get("face_count"))
    included_faces = _as_int(data.get("included_faces"))
    needs_name = status == "needs_name" or not (_as_text(data.get("display_label")) or _as_text(data.get("selected_name")))
    has_faces = face_count > 0 or included_faces > 0

    actions = [
        _action("select_group", "Select group", enabled=bool(group_id), category="navigation"),
        _action(
            "rename_group",
            "Set or change name",
            enabled=bool(group_id),
            category="review",
        ),
        _action(
            "accept_group",
            "Accept group",
            enabled=bool(group_id) and has_faces and not needs_name,
            category="review",
            blocked_reason="Set a name and keep at least one face before accepting." if needs_name or not has_faces else None,
        ),
        _action(
            "reject_group",
            "Reject group",
            enabled=bool(group_id),
            category="review",
            risk_level="medium",
            requires_confirmation=True,
        ),
        _action(
            "apply_ready_groups",
            "Apply ready groups",
            enabled=status == "ready_to_apply",
            category="apply",
            risk_level="high",
            requires_confirmation=True,
            blocked_reason=None if status == "ready_to_apply" else "Only ready groups can be applied to the people catalog.",
        ),
    ]
    return {
        "schema_version": PEOPLE_REVIEW_ACTIONS_SCHEMA_VERSION,
        "kind": "people_group_actions",
        "group_id": group_id or None,
        "status": status,
        "action_count": len(actions),
        "enabled_action_count": sum(1 for item in actions if item["enabled"]),
        "actions": actions,
    }


def build_people_face_actions(face: Mapping[str, Any] | None = None) -> dict[str, object]:
    data = _as_mapping(face)
    face_id = _as_text(data.get("face_id"))
    included = bool(data.get("include", data.get("included", True)))
    actions = [
        _action("select_face", "Select face", enabled=bool(face_id), category="navigation"),
        _action("include_face", "Mark as this person", enabled=bool(face_id) and not included, category="review"),
        _action("exclude_face", "Not this person", enabled=bool(face_id) and included, category="review"),
        _action("open_source", "Open source image", enabled=bool(data.get("path") or data.get("image_uri")), category="inspect"),
    ]
    return {
        "schema_version": PEOPLE_REVIEW_ACTIONS_SCHEMA_VERSION,
        "kind": "people_face_actions",
        "face_id": face_id or None,
        "included": included,
        "action_count": len(actions),
        "enabled_action_count": sum(1 for item in actions if item["enabled"]),
        "actions": actions,
    }


__all__ = [
    "PEOPLE_REVIEW_ACTIONS_SCHEMA_VERSION",
    "build_people_face_actions",
    "build_people_group_actions",
]
