from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from typing import Any

NOTIFICATION_SCHEMA_VERSION = "1.0"
NOTIFICATION_LEVELS = ("info", "success", "warning", "error")


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_notification(notification_id: str, title: str, message: str = "", *, level: str = "info", action: Mapping[str, Any] | None = None) -> dict[str, object]:
    normalized_level = str(level).strip().lower()
    if normalized_level not in NOTIFICATION_LEVELS:
        normalized_level = "info"
    payload: dict[str, object] = {
        "schema_version": NOTIFICATION_SCHEMA_VERSION,
        "id": str(notification_id),
        "title": str(title),
        "message": str(message),
        "level": normalized_level,
        "created_at_utc": _now_utc(),
        "dismissible": True,
    }
    if action:
        payload["action"] = dict(action)
    return payload


def build_notification_center(items: Iterable[Mapping[str, Any]] = ()) -> dict[str, object]:
    notifications = [dict(item) for item in items]
    level_summary: dict[str, int] = {}
    for item in notifications:
        level = str(item.get("level") or "info")
        level_summary[level] = level_summary.get(level, 0) + 1
    return {
        "schema_version": NOTIFICATION_SCHEMA_VERSION,
        "kind": "notification_center",
        "notification_count": len(notifications),
        "level_summary": dict(sorted(level_summary.items())),
        "items": notifications,
    }


def notifications_from_validation(validation_panel: Mapping[str, Any]) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for raw in validation_panel.get("messages", []) if isinstance(validation_panel.get("messages"), list) else []:
        if not isinstance(raw, Mapping):
            continue
        items.append(build_notification(str(raw.get("id") or len(items) + 1), str(raw.get("title") or raw.get("message") or "Validation"), str(raw.get("message") or ""), level=str(raw.get("level") or "info")))
    return items


__all__ = ["NOTIFICATION_LEVELS", "NOTIFICATION_SCHEMA_VERSION", "build_notification", "build_notification_center", "notifications_from_validation"]
