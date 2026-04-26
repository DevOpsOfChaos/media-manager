from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SIDEBAR_SCHEMA_VERSION = "1.0"


def _text(value: object) -> str:
    return str(value) if value is not None else ""


def build_qt_sidebar_button(item: Mapping[str, Any], *, index: int) -> dict[str, object]:
    page_id = _text(item.get("id") or item.get("page_id"))
    return {
        "id": page_id,
        "label": _text(item.get("label") or page_id.replace("-", " ").title()),
        "icon": _text(item.get("icon") or "circle"),
        "enabled": bool(item.get("enabled", True)),
        "active": bool(item.get("active", False)),
        "shortcut": f"Ctrl+{index + 1}" if index < 9 else None,
        "badge": item.get("badge"),
        "route": page_id,
        "object_name": "SidebarButtonActive" if item.get("active") else "SidebarButton",
    }


def build_qt_sidebar_model(navigation_items: Sequence[Mapping[str, Any]], *, title: str = "Media Manager") -> dict[str, object]:
    buttons = [build_qt_sidebar_button(item, index=index) for index, item in enumerate(navigation_items)]
    active = next((button for button in buttons if button.get("active")), None)
    return {
        "schema_version": SIDEBAR_SCHEMA_VERSION,
        "kind": "qt_sidebar_model",
        "title": title,
        "button_count": len(buttons),
        "active_page_id": active.get("id") if isinstance(active, Mapping) else None,
        "buttons": buttons,
        "footer_items": [
            {"id": "command_palette", "label": "Ctrl+K · Command palette"},
            {"id": "safe_mode", "label": "Safe preview-first mode"},
        ],
    }


__all__ = ["SIDEBAR_SCHEMA_VERSION", "build_qt_sidebar_button", "build_qt_sidebar_model"]
