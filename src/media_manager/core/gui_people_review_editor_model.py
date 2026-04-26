from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_i18n import translate
from .gui_modern_components import build_action_button, build_status_badge

PEOPLE_REVIEW_EDITOR_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _status_rank(status: object) -> int:
    return {
        "needs_name": 0,
        "needs_review": 1,
        "ready_to_apply": 2,
        "named_not_applied": 3,
        "all_faces_rejected": 4,
    }.get(str(status), 9)


def build_people_review_filters(*, language: str = "en") -> dict[str, object]:
    return {
        "schema_version": PEOPLE_REVIEW_EDITOR_SCHEMA_VERSION,
        "search_placeholder": translate("people.search", language=language),
        "filters": [
            {"id": "all", "label": translate("filter.all", language=language), "active": True},
            {"id": "needs_name", "label": translate("people.needs_name", language=language), "active": False},
            {"id": "needs_review", "label": translate("people.needs_review", language=language), "active": False},
            {"id": "ready_to_apply", "label": translate("people.ready_groups", language=language), "active": False},
        ],
    }


def build_people_review_editor_state(page_model: Mapping[str, Any], *, selected_group_id: str | None = None, language: str = "en") -> dict[str, object]:
    groups = [item for item in _list(page_model.get("groups")) if isinstance(item, Mapping)]
    groups.sort(key=lambda item: (_status_rank(item.get("status")), str(item.get("display_label") or item.get("group_id") or "").casefold()))
    selected = None
    if selected_group_id:
        selected = next((item for item in groups if str(item.get("group_id")) == str(selected_group_id)), None)
    if selected is None and groups:
        selected = groups[0]
    selected_id = str(selected.get("group_id")) if isinstance(selected, Mapping) and selected.get("group_id") else None
    return {
        "schema_version": PEOPLE_REVIEW_EDITOR_SCHEMA_VERSION,
        "kind": "people_review_editor_state",
        "filters": build_people_review_filters(language=language),
        "groups": [
            {
                "group_id": group.get("group_id"),
                "display_label": group.get("display_label") or translate("people.unknown_person", language=language),
                "status": group.get("status"),
                "status_badge": build_status_badge(group.get("status")),
                "face_count": group.get("face_count", 0),
                "included_faces": group.get("included_faces", 0),
                "excluded_faces": group.get("excluded_faces", 0),
                "selected": str(group.get("group_id")) == str(selected_id),
            }
            for group in groups
        ],
        "selected_group_id": selected_id,
        "selected_group": dict(selected) if isinstance(selected, Mapping) else None,
        "detail_actions": [
            build_action_button("accept_group", translate("people.action.accept_group", language=language), variant="primary", icon="check"),
            build_action_button("rename_group", translate("people.action.rename_group", language=language), icon="edit"),
            build_action_button("split_wrong_faces", translate("people.action.split_wrong_faces", language=language), icon="split"),
            build_action_button("apply_ready_groups", translate("people.action.apply_ready", language=language), variant="danger", risk_level="high", icon="shield-alert"),
        ],
        "empty_state": translate("people.empty", language=language) if not groups else None,
    }


__all__ = ["PEOPLE_REVIEW_EDITOR_SCHEMA_VERSION", "build_people_review_editor_state", "build_people_review_filters"]
