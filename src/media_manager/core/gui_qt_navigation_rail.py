from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

NAVIGATION_RAIL_SCHEMA_VERSION = "1.0"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _normalize_page_id(value: Any) -> str:
    text = str(value or "dashboard").strip().lower().replace("_", "-")
    return {"people": "people-review", "runs": "run-history", "new": "new-run"}.get(text, text or "dashboard")


def build_navigation_rail_item(item: Mapping[str, Any], *, active_page_id: str = "dashboard", index: int = 0) -> dict[str, object]:
    page_id = _normalize_page_id(item.get("id") or item.get("page_id"))
    label = str(item.get("label") or page_id.replace("-", " ").title())
    enabled = bool(item.get("enabled", True))
    return {
        "schema_version": NAVIGATION_RAIL_SCHEMA_VERSION,
        "kind": "navigation_rail_item",
        "id": page_id,
        "label": label,
        "icon": str(item.get("icon") or "circle"),
        "active": page_id == _normalize_page_id(active_page_id),
        "enabled": enabled,
        "shortcut": f"Ctrl+{index + 1}" if index < 9 else None,
        "tooltip": f"{label} ({f'Ctrl+{index + 1}' if index < 9 else 'open'})",
    }


def build_navigation_rail(items: Iterable[Mapping[str, Any]] | None = None, *, active_page_id: str = "dashboard", collapsed: bool = False) -> dict[str, object]:
    raw_items = list(items or [])
    normalized = [build_navigation_rail_item(_as_mapping(item), active_page_id=active_page_id, index=index) for index, item in enumerate(raw_items)]
    active = next((item for item in normalized if item.get("active")), None)
    return {
        "schema_version": NAVIGATION_RAIL_SCHEMA_VERSION,
        "kind": "navigation_rail",
        "collapsed": bool(collapsed),
        "width": 76 if collapsed else 280,
        "item_count": len(normalized),
        "active_page_id": active.get("id") if active else _normalize_page_id(active_page_id),
        "items": normalized,
        "enabled_count": sum(1 for item in normalized if item.get("enabled")),
    }


def build_navigation_rail_from_shell(shell_model: Mapping[str, Any], *, collapsed: bool = False) -> dict[str, object]:
    return build_navigation_rail(
        [_as_mapping(item) for item in _as_list(shell_model.get("navigation"))],
        active_page_id=str(shell_model.get("active_page_id") or "dashboard"),
        collapsed=collapsed,
    )


__all__ = ["NAVIGATION_RAIL_SCHEMA_VERSION", "build_navigation_rail", "build_navigation_rail_from_shell", "build_navigation_rail_item"]
