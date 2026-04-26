from __future__ import annotations

from collections.abc import Mapping
from typing import Any

NAVIGATION_SHELL_SCHEMA_VERSION = "1.0"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_navigation_shell_plan(shell_model: Mapping[str, Any]) -> dict[str, object]:
    nav_items = []
    for index, raw in enumerate(_list(shell_model.get("navigation"))):
        item = _mapping(raw)
        page_id = str(item.get("id") or item.get("page_id") or f"page-{index + 1}")
        nav_items.append({
            "id": page_id,
            "label": str(item.get("label") or page_id.replace("-", " ").title()),
            "active": bool(item.get("active", page_id == shell_model.get("active_page_id"))),
            "enabled": bool(item.get("enabled", True)),
            "shortcut": f"Ctrl+{index + 1}" if index < 9 else None,
        })
    return {
        "schema_version": NAVIGATION_SHELL_SCHEMA_VERSION,
        "kind": "navigation_shell_plan",
        "active_page_id": shell_model.get("active_page_id"),
        "rail": {"width": 280, "items": nav_items, "item_count": len(nav_items)},
        "content": {"page_id": shell_model.get("active_page_id"), "scrollable": True},
        "drawers": {"right": ["notifications", "diagnostics"], "bottom": ["command_palette"]},
    }


def summarize_navigation_shell_plan(plan: Mapping[str, Any]) -> dict[str, object]:
    rail = _mapping(plan.get("rail"))
    items = _list(rail.get("items"))
    return {
        "schema_version": NAVIGATION_SHELL_SCHEMA_VERSION,
        "active_page_id": plan.get("active_page_id"),
        "item_count": len(items),
        "enabled_count": sum(1 for item in items if _mapping(item).get("enabled")),
        "has_active": any(_mapping(item).get("active") for item in items),
    }


__all__ = ["NAVIGATION_SHELL_SCHEMA_VERSION", "build_navigation_shell_plan", "summarize_navigation_shell_plan"]
