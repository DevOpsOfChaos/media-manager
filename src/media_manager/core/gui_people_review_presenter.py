from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_action_bar_model import build_action_bar
from .gui_filter_bar import build_status_filter_bar
from .gui_presenter_state import build_presenter_state
from .gui_search_model import apply_search

PEOPLE_REVIEW_PRESENTER_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _group_label(group: Mapping[str, Any]) -> str:
    return str(group.get("display_label") or group.get("group_id") or "Unknown person")


def build_people_review_presenter(
    page_model: Mapping[str, Any],
    *,
    selected_group_id: str | None = None,
    query: str = "",
    language: str = "en",
) -> dict[str, object]:
    groups = [dict(group) for group in _list(page_model.get("groups")) if isinstance(group, Mapping)]
    filtered = apply_search(groups, query=query, fields=("display_label", "group_id", "status"))
    selected_id = selected_group_id or page_model.get("selected_group_id")
    selected = next((group for group in filtered if str(group.get("group_id")) == str(selected_id)), None)
    if selected is None and filtered:
        selected = filtered[0]
    selected_id = str(selected.get("group_id")) if isinstance(selected, Mapping) and selected.get("group_id") else None
    actions = [
        {"id": "accept_group", "label": "Accept group", "enabled": selected is not None, "recommended": True},
        {"id": "rename_group", "label": "Rename", "enabled": selected is not None},
        {"id": "reject_selected", "label": "Reject selected faces", "enabled": selected is not None},
        {"id": "apply_ready", "label": "Apply ready groups", "enabled": bool(page_model.get("overview")), "risk_level": "high", "requires_confirmation": True},
    ]
    return {
        "schema_version": PEOPLE_REVIEW_PRESENTER_SCHEMA_VERSION,
        "kind": "people_review_presenter",
        "page_id": "people-review",
        "title": page_model.get("title"),
        "overview": dict(_mapping(page_model.get("overview"))),
        "master": {
            "groups": filtered,
            "group_count": len(filtered),
            "selected_group_id": selected_id,
            "status_filter": build_status_filter_bar(filtered),
            "empty": len(filtered) == 0,
        },
        "detail": {
            "group": dict(selected) if isinstance(selected, Mapping) else None,
            "title": _group_label(selected) if isinstance(selected, Mapping) else "No group selected",
            "face_count": selected.get("face_count", 0) if isinstance(selected, Mapping) else 0,
        },
        "action_bar": build_action_bar(actions),
        "presenter": build_presenter_state(page_model={**dict(page_model), "groups": filtered, "selected_group_id": selected_id}, actions=actions, language=language),
    }


__all__ = ["PEOPLE_REVIEW_PRESENTER_SCHEMA_VERSION", "build_people_review_presenter"]
