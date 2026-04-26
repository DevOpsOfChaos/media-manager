from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .gui_viewport_model import choose_column_count, normalize_viewport

RESPONSIVE_LAYOUT_SCHEMA_VERSION = "1.0"


def build_responsive_grid(
    items: Iterable[Mapping[str, Any]],
    *,
    viewport: Mapping[str, Any] | None = None,
    item_kind: str = "card",
    max_columns: int = 5,
) -> dict[str, object]:
    item_list = [dict(item) for item in items]
    normalized_viewport = normalize_viewport(viewport)
    columns = choose_column_count(normalized_viewport, item_count=len(item_list), max_columns=max_columns)
    placements: list[dict[str, object]] = []
    for index, item in enumerate(item_list):
        placements.append(
            {
                "index": index,
                "id": item.get("id") or item.get("group_id") or item.get("face_id") or f"item-{index + 1}",
                "row": index // columns,
                "column": index % columns,
                "column_span": 1,
                "item_kind": item_kind,
                "item": item,
            }
        )
    return {
        "schema_version": RESPONSIVE_LAYOUT_SCHEMA_VERSION,
        "kind": "responsive_grid",
        "viewport": normalized_viewport,
        "item_kind": item_kind,
        "item_count": len(item_list),
        "columns": columns,
        "row_count": (len(item_list) + columns - 1) // columns if item_list else 0,
        "placements": placements,
    }


def build_responsive_regions(page_id: str, *, viewport: Mapping[str, Any] | None = None) -> dict[str, object]:
    normalized = normalize_viewport(viewport)
    compact = bool(normalized["is_compact"])
    if page_id == "people-review":
        regions = ["toolbar", "queue", "detail"] if compact else ["toolbar", "queue_sidebar", "detail", "activity"]
    elif page_id == "dashboard":
        regions = ["hero", "cards", "activity"]
    else:
        regions = ["toolbar", "content"]
    return {
        "schema_version": RESPONSIVE_LAYOUT_SCHEMA_VERSION,
        "kind": "responsive_regions",
        "page_id": page_id,
        "viewport": normalized,
        "compact": compact,
        "regions": regions,
    }


__all__ = ["RESPONSIVE_LAYOUT_SCHEMA_VERSION", "build_responsive_grid", "build_responsive_regions"]
