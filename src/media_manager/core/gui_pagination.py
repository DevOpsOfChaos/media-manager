from __future__ import annotations

from collections.abc import Sequence
from typing import Any

PAGINATION_SCHEMA_VERSION = "1.0"


def clamp_page(page: int, *, total_items: int, page_size: int) -> int:
    safe_size = max(1, int(page_size))
    total_pages = max(1, (max(0, int(total_items)) + safe_size - 1) // safe_size)
    return max(1, min(int(page), total_pages))


def build_pagination_state(items: Sequence[Any], *, page: int = 1, page_size: int = 50) -> dict[str, object]:
    safe_size = max(1, int(page_size))
    total_items = len(items)
    current = clamp_page(page, total_items=total_items, page_size=safe_size)
    start = (current - 1) * safe_size
    end = start + safe_size
    page_items = list(items[start:end])
    total_pages = max(1, (total_items + safe_size - 1) // safe_size)
    return {
        "schema_version": PAGINATION_SCHEMA_VERSION,
        "kind": "gui_pagination_state",
        "page": current,
        "page_size": safe_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "start_index": start,
        "end_index": min(end, total_items),
        "returned_count": len(page_items),
        "has_previous": current > 1,
        "has_next": current < total_pages,
        "items": page_items,
    }


def page_summary_text(pagination: dict[str, object]) -> str:
    total = pagination.get("total_items", 0)
    if not total:
        return "0 items"
    start = int(pagination.get("start_index", 0)) + 1
    end = int(pagination.get("end_index", 0))
    return f"{start}-{end} of {total}"


__all__ = ["PAGINATION_SCHEMA_VERSION", "build_pagination_state", "clamp_page", "page_summary_text"]
