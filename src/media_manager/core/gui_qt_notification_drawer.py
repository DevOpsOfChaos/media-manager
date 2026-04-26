from __future__ import annotations

from collections.abc import Mapping
from typing import Any

NOTIFICATION_DRAWER_SCHEMA_VERSION = "1.0"
_ORDER = {"error": 0, "warning": 1, "success": 2, "info": 3}


def build_qt_notification_drawer(notifications: list[Mapping[str, Any]] | None = None, *, limit: int = 20) -> dict[str, object]:
    items = [dict(item) for item in notifications or []]
    items.sort(key=lambda item: (_ORDER.get(str(item.get("level") or "info"), 9), str(item.get("created_at_utc") or "")), reverse=False)
    returned = items[: max(0, int(limit))]
    return {"schema_version": NOTIFICATION_DRAWER_SCHEMA_VERSION, "notification_count": len(items), "returned_count": len(returned), "truncated": len(returned) < len(items), "items": returned, "has_errors": any(item.get("level") == "error" for item in items)}


__all__ = ["NOTIFICATION_DRAWER_SCHEMA_VERSION", "build_qt_notification_drawer"]
