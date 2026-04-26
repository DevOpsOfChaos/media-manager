from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
from typing import Any

EVENT_BUS_SCHEMA_VERSION = "1.0"


def build_gui_event(event_type: str, *, payload: Mapping[str, Any] | None = None, source: str = "gui", sequence: int | None = None) -> dict[str, object]:
    body = dict(payload or {})
    token = f"{sequence}|{source}|{event_type}|{sorted(body.items())}"
    event_id = hashlib.sha1(token.encode("utf-8")).hexdigest()[:16]
    return {
        "schema_version": EVENT_BUS_SCHEMA_VERSION,
        "event_id": f"event-{event_id}",
        "type": event_type,
        "source": source,
        "sequence": sequence,
        "payload": body,
        "executes_immediately": False,
    }


def build_event_queue(events: Iterable[Mapping[str, Any]] = ()) -> dict[str, object]:
    items = [dict(item) for item in events]
    type_summary: dict[str, int] = {}
    for item in items:
        key = str(item.get("type") or "unknown")
        type_summary[key] = type_summary.get(key, 0) + 1
    return {
        "schema_version": EVENT_BUS_SCHEMA_VERSION,
        "kind": "gui_event_queue",
        "event_count": len(items),
        "type_summary": dict(sorted(type_summary.items())),
        "events": items,
    }


def append_gui_event(queue: Mapping[str, Any], event: Mapping[str, Any]) -> dict[str, object]:
    events = queue.get("events") if isinstance(queue.get("events"), list) else []
    return build_event_queue([*events, dict(event)])


__all__ = ["EVENT_BUS_SCHEMA_VERSION", "append_gui_event", "build_event_queue", "build_gui_event"]
