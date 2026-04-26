from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

CARD_GRID_SCHEMA_VERSION = "1.0"

_DENSITY_COLUMNS = {
    "compact": 4,
    "comfortable": 3,
    "spacious": 2,
}


def _as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _card_from_payload(raw: Mapping[str, Any], *, index: int) -> dict[str, object]:
    metrics = _as_mapping(raw.get("metrics"))
    actions = _as_list(raw.get("actions"))
    return {
        "kind": "qt_card_plan",
        "card_id": str(raw.get("id") or f"card-{index + 1}"),
        "title": str(raw.get("title") or raw.get("label") or "Card"),
        "subtitle": str(raw.get("subtitle") or raw.get("description") or ""),
        "metrics": dict(metrics),
        "metric_count": len(metrics),
        "actions": [dict(item) for item in actions if isinstance(item, Mapping)],
        "qt": {"widget": "QFrame", "object_name": "Card"},
    }


def build_qt_card_grid_plan(
    cards: Iterable[Mapping[str, Any]],
    *,
    density: str = "comfortable",
    max_cards: int = 12,
    columns: int | None = None,
) -> dict[str, object]:
    all_cards = [_card_from_payload(dict(item), index=index) for index, item in enumerate(cards)]
    limit = max(0, int(max_cards))
    visible_cards = all_cards[:limit]
    column_count = max(1, int(columns or _DENSITY_COLUMNS.get(str(density), 3)))
    placements = []
    for index, card in enumerate(visible_cards):
        placements.append(
            {
                "card_id": card["card_id"],
                "row": index // column_count,
                "column": index % column_count,
                "row_span": 1,
                "column_span": 1,
            }
        )
    return {
        "schema_version": CARD_GRID_SCHEMA_VERSION,
        "kind": "qt_card_grid_plan",
        "density": density,
        "columns": column_count,
        "card_count": len(all_cards),
        "visible_card_count": len(visible_cards),
        "truncated": len(all_cards) > len(visible_cards),
        "cards": visible_cards,
        "placements": placements,
    }


def summarize_card_grid(plan: Mapping[str, Any]) -> dict[str, object]:
    return {
        "card_count": plan.get("card_count", 0),
        "visible_card_count": plan.get("visible_card_count", 0),
        "columns": plan.get("columns", 0),
        "truncated": bool(plan.get("truncated", False)),
    }


__all__ = ["CARD_GRID_SCHEMA_VERSION", "build_qt_card_grid_plan", "summarize_card_grid"]
