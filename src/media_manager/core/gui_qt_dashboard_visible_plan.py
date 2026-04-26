from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_card_grid_plan import build_qt_card_grid_plan
from .gui_qt_section_plan import build_qt_section_plan

DASHBOARD_VISIBLE_PLAN_SCHEMA_VERSION = "1.0"


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_dashboard_visible_plan(page_model: Mapping[str, Any], *, density: str = "comfortable") -> dict[str, object]:
    hero = _as_mapping(page_model.get("hero"))
    activity = _as_mapping(page_model.get("activity"))
    card_grid = build_qt_card_grid_plan(
        [item for item in _as_list(page_model.get("cards")) if isinstance(item, Mapping)],
        density=density,
        max_cards=9,
    )
    hero_section = build_qt_section_plan(
        "dashboard-hero",
        title=str(hero.get("title") or page_model.get("title") or "Dashboard"),
        subtitle=str(hero.get("subtitle") or page_model.get("description") or ""),
        variant="hero",
        children=[
            {
                "kind": "metric_strip",
                "metrics": dict(_as_mapping(hero.get("metrics"))),
            }
        ],
    )
    activity_section = build_qt_section_plan(
        "dashboard-activity",
        title=str(activity.get("title") or "Activity"),
        subtitle=str(activity.get("subtitle") or ""),
        variant="activity",
        children=[{"kind": "activity_item", **dict(item)} for item in _as_list(activity.get("items")) if isinstance(item, Mapping)],
    )
    return {
        "schema_version": DASHBOARD_VISIBLE_PLAN_SCHEMA_VERSION,
        "kind": "qt_dashboard_visible_plan",
        "page_id": "dashboard",
        "title": page_model.get("title", "Dashboard"),
        "layout": "hero_grid_activity",
        "sections": [hero_section, {"section_id": "dashboard-cards", "kind": "card_grid_section", "grid": card_grid}, activity_section],
        "card_grid": card_grid,
        "summary": {
            "card_count": card_grid["card_count"],
            "activity_count": len(_as_list(activity.get("items"))),
            "has_hero": bool(hero_section.get("title")),
        },
    }


__all__ = ["DASHBOARD_VISIBLE_PLAN_SCHEMA_VERSION", "build_qt_dashboard_visible_plan"]
