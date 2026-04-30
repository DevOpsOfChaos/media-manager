from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REVIEW_WORKBENCH_TABLE_MODEL_KIND = "ui_review_workbench_table_model"


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _normalize_page(value: object, *, default: int = 1) -> int:
    return max(1, _as_int(value, default))


def _normalize_page_size(value: object, *, default: int = 20) -> int:
    return min(100, max(1, _as_int(value, default)))


def build_review_workbench_table_columns() -> list[dict[str, object]]:
    return [
        {"id": "title", "label": "Lane", "role": "primary_text", "sortable": True},
        {"id": "status", "label": "Status", "role": "status_badge", "sortable": True},
        {"id": "attention_count", "label": "Needs review", "role": "number", "sortable": True},
        {"id": "item_count", "label": "Items", "role": "number", "sortable": True},
        {"id": "latest_run_path", "label": "Latest run", "role": "path", "sortable": False},
        {"id": "page_id", "label": "Route", "role": "route", "sortable": False},
    ]


def build_review_workbench_table_row(
    lane: Mapping[str, Any],
    *,
    selected_lane_id: str | None = None,
) -> dict[str, object]:
    lane_id = str(lane.get("lane_id") or "")
    status = str(lane.get("status") or "empty")
    attention_count = _as_int(lane.get("attention_count"))
    item_count = _as_int(lane.get("item_count"))
    selected = bool(lane_id and lane_id == str(selected_lane_id or ""))
    return {
        "kind": "ui_review_workbench_table_row",
        "id": lane_id,
        "lane_id": lane_id,
        "title": str(lane.get("title") or lane_id),
        "description": str(lane.get("description") or ""),
        "status": status,
        "attention_count": attention_count,
        "item_count": item_count,
        "latest_run_path": str(lane.get("latest_run_path") or ""),
        "page_id": str(lane.get("page_id") or ""),
        "selected": selected,
        "has_attention": attention_count > 0,
        "enabled": True,
        "executes_immediately": False,
    }


def paginate_review_workbench_lanes(
    lanes: list[Mapping[str, Any]],
    *,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    normalized_page_size = _normalize_page_size(page_size)
    total_count = len(lanes)
    page_count = max(1, (total_count + normalized_page_size - 1) // normalized_page_size)
    normalized_page = min(_normalize_page(page), page_count)
    start = (normalized_page - 1) * normalized_page_size
    end = start + normalized_page_size
    return {
        "kind": "ui_review_workbench_table_pagination",
        "page": normalized_page,
        "page_size": normalized_page_size,
        "page_count": page_count,
        "total_count": total_count,
        "start_index": start,
        "end_index": min(end, total_count),
        "has_previous": normalized_page > 1,
        "has_next": normalized_page < page_count,
        "visible_lane_ids": [str(lane.get("lane_id") or "") for lane in lanes[start:end] if lane.get("lane_id")],
        "executes_commands": False,
    }


def build_review_workbench_table_model(
    lanes: list[Mapping[str, Any]],
    *,
    selected_lane_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    pagination = paginate_review_workbench_lanes(lanes, page=page, page_size=page_size)
    start = int(pagination["start_index"])
    end = int(pagination["end_index"])
    visible = lanes[start:end]
    rows = [build_review_workbench_table_row(lane, selected_lane_id=selected_lane_id) for lane in visible]
    return {
        "kind": REVIEW_WORKBENCH_TABLE_MODEL_KIND,
        "columns": build_review_workbench_table_columns(),
        "rows": rows,
        "pagination": pagination,
        "selected_lane_id": selected_lane_id or None,
        "summary": {
            "row_count": len(rows),
            "total_count": len(lanes),
            "selected_row_count": sum(1 for row in rows if row["selected"]),
            "attention_row_count": sum(1 for row in rows if row["has_attention"]),
        },
        "capabilities": {
            "headless_testable": True,
            "requires_pyside6": False,
            "opens_window": False,
            "executes_commands": False,
        },
    }


__all__ = [
    "REVIEW_WORKBENCH_TABLE_MODEL_KIND",
    "build_review_workbench_table_columns",
    "build_review_workbench_table_model",
    "build_review_workbench_table_row",
    "paginate_review_workbench_lanes",
]
