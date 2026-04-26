from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_helpers import as_list, as_mapping, as_text, compact_metrics, widget

QT_DASHBOARD_SCHEMA_VERSION = "1.0"


def build_qt_dashboard_page_plan(page_model: Mapping[str, Any]) -> dict[str, object]:
    hero = as_mapping(page_model.get("hero"))
    widgets: list[dict[str, object]] = [
        widget(
            "hero_panel",
            widget_id="dashboard.hero",
            title=as_text(hero.get("title"), as_text(page_model.get("title"), "Dashboard")),
            subtitle=as_text(hero.get("subtitle"), as_text(page_model.get("description"))),
            metrics=compact_metrics(as_mapping(hero.get("metrics"))),
            region="hero",
        )
    ]
    for index, raw_card in enumerate(as_list(page_model.get("cards"))):
        card = as_mapping(raw_card)
        widgets.append(
            widget(
                "metric_card",
                widget_id=f"dashboard.card.{as_text(card.get('id'), str(index))}",
                title=as_text(card.get("title")),
                subtitle=as_text(card.get("subtitle")),
                metrics=compact_metrics(as_mapping(card.get("metrics"))),
                actions=as_list(card.get("actions"))[:3],
                region="cards",
            )
        )
    activity = as_mapping(page_model.get("activity"))
    if activity:
        widgets.append(
            widget(
                "activity_panel",
                widget_id="dashboard.activity",
                title=as_text(activity.get("title"), "Recent activity"),
                items=as_list(activity.get("items"))[:8],
                region="activity",
            )
        )
    return {
        "schema_version": QT_DASHBOARD_SCHEMA_VERSION,
        "kind": "qt_dashboard_page_plan",
        "page_id": "dashboard",
        "layout": "dashboard_responsive_grid",
        "widget_count": len(widgets),
        "widgets": widgets,
    }


__all__ = ["QT_DASHBOARD_SCHEMA_VERSION", "build_qt_dashboard_page_plan"]
