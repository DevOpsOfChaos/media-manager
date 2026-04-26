from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LIST_DETAIL_SCHEMA_VERSION = "1.0"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_list_detail_plan(items: list[Mapping[str, Any]], *, selected_id: str | None = None, id_key: str = "id", title_key: str = "title") -> dict[str, object]:
    rows = []
    selected = None
    fallback_id = str(items[0].get(id_key)) if items else None
    current = selected_id or fallback_id
    for item in items:
        row_id = str(item.get(id_key) or "")
        row = {"id": row_id, "title": str(item.get(title_key) or item.get("display_label") or row_id), "selected": row_id == current, "raw": dict(item)}
        if row["selected"]:
            selected = row
        rows.append(row)
    return {"schema_version": LIST_DETAIL_SCHEMA_VERSION, "item_count": len(rows), "selected_id": current, "rows": rows, "detail": selected, "has_selection": selected is not None}


def build_people_group_list_detail(page_model: Mapping[str, Any]) -> dict[str, object]:
    groups = [item for item in _list(page_model.get("groups")) if isinstance(item, Mapping)]
    return build_qt_list_detail_plan(groups, selected_id=page_model.get("selected_group_id"), id_key="group_id", title_key="display_label")


__all__ = ["LIST_DETAIL_SCHEMA_VERSION", "build_qt_list_detail_plan", "build_people_group_list_detail"]
