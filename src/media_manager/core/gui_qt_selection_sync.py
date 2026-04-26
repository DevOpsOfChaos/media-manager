from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

SELECTION_SYNC_SCHEMA_VERSION = "1.0"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def normalize_selection_state(state: Mapping[str, Any] | None = None) -> dict[str, object]:
    state = _as_mapping(state)
    return {
        "schema_version": SELECTION_SYNC_SCHEMA_VERSION,
        "page_id": str(state.get("page_id") or "dashboard"),
        "selected_group_id": state.get("selected_group_id"),
        "selected_face_ids": [str(item) for item in _as_list(state.get("selected_face_ids"))],
        "selected_run_id": state.get("selected_run_id"),
        "selected_profile_id": state.get("selected_profile_id"),
    }


def apply_selection_event(selection: Mapping[str, Any] | None, event: Mapping[str, Any]) -> dict[str, object]:
    payload = normalize_selection_state(selection)
    event_type = str(event.get("type") or "")
    if event_type == "select_group":
        payload["selected_group_id"] = event.get("group_id")
        payload["selected_face_ids"] = []
        payload["page_id"] = "people-review"
    elif event_type == "select_face":
        face_id = str(event.get("face_id") or "")
        if face_id:
            payload["selected_face_ids"] = [face_id]
        payload["page_id"] = "people-review"
    elif event_type == "toggle_face":
        face_id = str(event.get("face_id") or "")
        current = set(str(item) for item in payload["selected_face_ids"])
        if face_id in current:
            current.remove(face_id)
        elif face_id:
            current.add(face_id)
        payload["selected_face_ids"] = sorted(current)
        payload["page_id"] = "people-review"
    elif event_type == "select_run":
        payload["selected_run_id"] = event.get("run_id")
        payload["page_id"] = "run-history"
    elif event_type == "clear":
        payload = normalize_selection_state({"page_id": payload.get("page_id")})
    payload["last_event_type"] = event_type
    return payload


def sync_selection_with_available_groups(selection: Mapping[str, Any], groups: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    payload = normalize_selection_state(selection)
    available = {str(group.get("group_id")) for group in groups if group.get("group_id")}
    if payload.get("selected_group_id") and str(payload["selected_group_id"]) not in available:
        payload["selected_group_id"] = None
        payload["selected_face_ids"] = []
        payload["sync_warning"] = "selected_group_missing"
    return payload


__all__ = [
    "SELECTION_SYNC_SCHEMA_VERSION",
    "apply_selection_event",
    "normalize_selection_state",
    "sync_selection_with_available_groups",
]
