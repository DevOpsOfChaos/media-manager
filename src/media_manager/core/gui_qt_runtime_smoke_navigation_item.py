from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_NAVIGATION_ITEM_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_navigation_item(route_model: Mapping[str, Any]) -> dict[str, object]:
    """Build a shell navigation item for the runtime smoke route."""

    badge = _mapping(route_model.get("badge"))
    guards = _mapping(route_model.get("guards"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_NAVIGATION_ITEM_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_navigation_item",
        "id": route_model.get("route_id") or "runtime-smoke",
        "page_id": route_model.get("page_id") or "runtime-smoke",
        "label": route_model.get("label") or "Runtime Smoke",
        "description": route_model.get("description"),
        "enabled": bool(route_model.get("enabled")),
        "visible": bool(route_model.get("visible", True)),
        "badge": {
            "text": "Ready" if badge.get("state") == "ready" else "Needs attention",
            "state": badge.get("state"),
            "problem_count": int(badge.get("problem_count") or 0),
        },
        "security": {
            "local_only": bool(guards.get("local_only", True)),
            "opens_window": bool(guards.get("opens_window", False)),
            "executes_commands": bool(guards.get("executes_commands", False)),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_NAVIGATION_ITEM_SCHEMA_VERSION", "build_qt_runtime_smoke_navigation_item"]
