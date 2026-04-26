from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_widget_specs import build_card_spec, build_text_spec, build_widget_spec, summarize_widget_tree

DASHBOARD_RENDERER_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_dashboard_render_spec(page_model: Mapping[str, Any]) -> dict[str, object]:
    hero = _mapping(page_model.get("hero"))
    cards = [item for item in _list(page_model.get("cards")) if isinstance(item, Mapping)]
    card_widgets = [
        build_card_spec(
            str(card.get("id") or f"card-{index}"),
            str(card.get("title") or card.get("id") or f"Card {index}"),
            subtitle=str(card.get("subtitle") or ""),
            metrics=_mapping(card.get("metrics")),
            actions=[item for item in _list(card.get("actions")) if isinstance(item, Mapping)],
        )
        for index, card in enumerate(cards, start=1)
    ]
    root = build_widget_spec(
        "dashboard-root",
        "section",
        title=str(page_model.get("title") or "Dashboard"),
        slots={
            "hero": build_widget_spec(
                "dashboard-hero",
                "hero",
                title=str(hero.get("title") or page_model.get("title") or "Dashboard"),
                props={"subtitle": hero.get("subtitle") or page_model.get("description") or ""},
            ),
            "cards": build_widget_spec("dashboard-card-grid", "card_grid", children=card_widgets),
            "activity": build_text_spec("dashboard-activity", str(_mapping(page_model.get("activity")).get("title") or "")),
        },
    )
    return {
        "schema_version": DASHBOARD_RENDERER_SCHEMA_VERSION,
        "kind": "dashboard_render_spec",
        "page_id": page_model.get("page_id", "dashboard"),
        "root": root,
        "summary": summarize_widget_tree(root),
    }


__all__ = ["DASHBOARD_RENDERER_SCHEMA_VERSION", "build_dashboard_render_spec"]
