from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

TABLE_VISIBLE_PLAN_SCHEMA_VERSION = "1.0"


def _text(value: object) -> str:
    if isinstance(value, Mapping):
        for key in ("value", "path", "label", "title", "id"):
            if value.get(key) is not None:
                return str(value.get(key))
        return str(dict(value))
    if value is None:
        return ""
    return str(value)


def _normalize_columns(columns: Iterable[object], rows: list[Mapping[str, Any]]) -> list[str]:
    explicit = [str(item) for item in columns if str(item).strip()]
    if explicit:
        return explicit
    keys: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in keys:
                keys.append(str(key))
    return keys


def build_qt_table_visible_plan(
    *,
    table_id: str,
    columns: Iterable[object] = (),
    rows: Iterable[Mapping[str, Any]] = (),
    max_rows: int = 200,
    empty_title: str = "No rows",
) -> dict[str, object]:
    row_list = [dict(row) for row in rows]
    column_list = _normalize_columns(columns, row_list)
    limit = max(0, int(max_rows))
    visible_rows = row_list[:limit]
    cells = []
    for row_index, row in enumerate(visible_rows):
        cell_row = []
        for column in column_list:
            cell_row.append(
                {
                    "column": column,
                    "text": _text(row.get(column)),
                    "raw_value_type": type(row.get(column)).__name__,
                }
            )
        cells.append({"row_index": row_index, "cells": cell_row})
    return {
        "schema_version": TABLE_VISIBLE_PLAN_SCHEMA_VERSION,
        "kind": "qt_table_visible_plan",
        "table_id": str(table_id),
        "columns": column_list,
        "column_count": len(column_list),
        "row_count": len(row_list),
        "visible_row_count": len(visible_rows),
        "truncated": len(row_list) > len(visible_rows),
        "rows": cells,
        "empty_state": {"title": empty_title, "visible": not bool(row_list)},
        "qt": {"widget": "QTableWidget", "selection_behavior": "SelectRows"},
    }


def table_plan_has_rows(plan: Mapping[str, Any]) -> bool:
    return int(plan.get("visible_row_count", 0) or 0) > 0


__all__ = ["TABLE_VISIBLE_PLAN_SCHEMA_VERSION", "build_qt_table_visible_plan", "table_plan_has_rows"]
