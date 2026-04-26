from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

STATE_REDUCER_SCHEMA_VERSION = "1.0"


def reduce_gui_state(state: Mapping[str, Any], event: Mapping[str, Any]) -> dict[str, object]:
    result: dict[str, object] = dict(state)
    event_type = str(event.get("type") or "")
    payload = event.get("payload") if isinstance(event.get("payload"), Mapping) else {}
    if event_type == "navigate":
        result["active_page_id"] = str(payload.get("page_id") or result.get("active_page_id") or "dashboard")
    elif event_type == "search.set":
        result["query"] = str(payload.get("query") or "")
    elif event_type == "people.group.select":
        result["selected_group_id"] = str(payload.get("group_id") or "")
        if payload.get("face_id") is not None:
            result["selected_face_id"] = str(payload.get("face_id"))
    elif event_type == "notification.add":
        notifications = list(result.get("notifications") if isinstance(result.get("notifications"), list) else [])
        notifications.append(dict(payload))
        result["notifications"] = notifications
    return result


def apply_gui_events(state: Mapping[str, Any], events: Iterable[Mapping[str, Any]]) -> dict[str, object]:
    result: Mapping[str, Any] = dict(state)
    applied = 0
    for event in events:
        result = reduce_gui_state(result, event)
        applied += 1
    return {**dict(result), "schema_version": STATE_REDUCER_SCHEMA_VERSION, "applied_event_count": applied}


__all__ = ["STATE_REDUCER_SCHEMA_VERSION", "apply_gui_events", "reduce_gui_state"]
