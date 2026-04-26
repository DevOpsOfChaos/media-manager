from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any

AUDIT_SCHEMA_VERSION = "1.0"


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _text(value: object) -> str:
    return value if isinstance(value, str) else ""


def build_review_audit_event(
    event_type: str,
    *,
    group_id: str | None = None,
    face_id: str | None = None,
    actor: str = "local-user",
    details: Mapping[str, Any] | None = None,
    created_at_utc: str | None = None,
) -> dict[str, object]:
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "kind": "people_review_audit_event",
        "event_type": _text(event_type) or "unknown",
        "group_id": group_id or None,
        "face_id": face_id or None,
        "actor": _text(actor) or "local-user",
        "created_at_utc": created_at_utc or _now_utc(),
        "details": dict(details or {}),
    }


def append_review_audit_event(log_payload: Mapping[str, Any] | None, event: Mapping[str, Any]) -> dict[str, object]:
    events = []
    if isinstance(log_payload, Mapping) and isinstance(log_payload.get("events"), list):
        events = [item for item in log_payload["events"] if isinstance(item, Mapping)]
    events.append(dict(event))
    return build_review_audit_log(events)


def build_review_audit_log(events: Iterable[Mapping[str, Any]] = ()) -> dict[str, object]:
    items = [dict(item) for item in events]
    by_type: dict[str, int] = {}
    for item in items:
        event_type = _text(item.get("event_type")) or "unknown"
        by_type[event_type] = by_type.get(event_type, 0) + 1
    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "kind": "people_review_audit_log",
        "event_count": len(items),
        "event_type_summary": dict(sorted(by_type.items())),
        "events": items,
    }


def recent_review_events(log_payload: Mapping[str, Any], *, limit: int = 20) -> list[dict[str, object]]:
    events = log_payload.get("events") if isinstance(log_payload, Mapping) else []
    if not isinstance(events, list):
        return []
    return [dict(item) for item in events[-max(0, int(limit)):][::-1] if isinstance(item, Mapping)]


__all__ = [
    "AUDIT_SCHEMA_VERSION",
    "append_review_audit_event",
    "build_review_audit_event",
    "build_review_audit_log",
    "recent_review_events",
]
