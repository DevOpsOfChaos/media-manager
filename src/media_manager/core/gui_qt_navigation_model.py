from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_helpers import as_list, as_mapping, as_text

QT_NAVIGATION_SCHEMA_VERSION = "1.0"

_DEFAULT_SHORTCUTS = {
    "dashboard": "Ctrl+1",
    "new-run": "Ctrl+2",
    "people-review": "Ctrl+3",
    "run-history": "Ctrl+4",
    "profiles": "Ctrl+5",
    "settings": "Ctrl+,",
}


def normalize_qt_navigation_item(item: Mapping[str, Any], *, active_page_id: str) -> dict[str, object]:
    page_id = as_text(item.get("id") or item.get("page_id"))
    label = as_text(item.get("label"), page_id.replace("-", " ").title())
    enabled = bool(item.get("enabled", True))
    return {
        "schema_version": QT_NAVIGATION_SCHEMA_VERSION,
        "id": page_id,
        "label": label,
        "icon": as_text(item.get("icon"), "circle"),
        "enabled": enabled,
        "active": page_id == active_page_id,
        "shortcut": as_text(item.get("shortcut"), _DEFAULT_SHORTCUTS.get(page_id, "")),
        "button_role": "primary_nav" if page_id == active_page_id else "nav",
    }


def build_qt_navigation_model(shell_model: Mapping[str, Any]) -> dict[str, object]:
    active_page_id = as_text(shell_model.get("active_page_id"), "dashboard")
    items = [
        normalize_qt_navigation_item(as_mapping(item), active_page_id=active_page_id)
        for item in as_list(shell_model.get("navigation"))
        if as_mapping(item).get("id") or as_mapping(item).get("page_id")
    ]
    return {
        "schema_version": QT_NAVIGATION_SCHEMA_VERSION,
        "kind": "qt_navigation_model",
        "active_page_id": active_page_id,
        "item_count": len(items),
        "items": items,
        "enabled_count": sum(1 for item in items if item.get("enabled") is True),
        "active_item": next((item for item in items if item.get("active") is True), None),
    }


__all__ = ["QT_NAVIGATION_SCHEMA_VERSION", "build_qt_navigation_model", "normalize_qt_navigation_item"]
