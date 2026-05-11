from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_visible_page_adapter import build_qt_visible_page_plan, visible_page_plan_summary

VISIBLE_DESKTOP_PLAN_SCHEMA_VERSION = "1.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_visible_desktop_plan(shell_model: Mapping[str, Any]) -> dict[str, object]:
    page_model = _as_mapping(shell_model.get("page"))
    layout = _as_mapping(shell_model.get("layout"))
    page_plan = build_qt_visible_page_plan(page_model, density=str(layout.get("density") or "comfortable"))
    navigation_items = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(_as_list(shell_model.get("navigation"))):
        if not isinstance(raw, Mapping):
            continue
        page_id = str(raw.get("id") or "").strip()
        if not page_id or page_id in seen_ids:
            continue
        seen_ids.add(page_id)
        navigation_items.append(
            {
                "id": page_id,
                "label": raw.get("label"),
                "active": bool(raw.get("active")),
                "enabled": bool(raw.get("enabled", True)),
                "shortcut": f"Ctrl+{index + 1}" if index < 9 else None,
            }
        )
    return {
        "schema_version": VISIBLE_DESKTOP_PLAN_SCHEMA_VERSION,
        "kind": "qt_visible_desktop_plan",
        "window": dict(_as_mapping(shell_model.get("window"))),
        "theme": dict(_as_mapping(shell_model.get("theme"))),
        "active_page_id": shell_model.get("active_page_id"),
        "navigation": navigation_items,
        "page": page_plan,
        "status_bar": dict(_as_mapping(shell_model.get("status_bar"))),
        "summary": {
            **visible_page_plan_summary(page_plan),
            "navigation_count": len(navigation_items),
            "active_navigation_count": sum(1 for item in navigation_items if item.get("active")),
        },
    }


def desktop_plan_is_ready(plan: Mapping[str, Any]) -> bool:
    summary = _as_mapping(plan.get("summary"))
    return bool(summary.get("ready_for_qt")) and int(summary.get("navigation_count", 0) or 0) >= 0


__all__ = ["VISIBLE_DESKTOP_PLAN_SCHEMA_VERSION", "build_qt_visible_desktop_plan", "desktop_plan_is_ready"]
