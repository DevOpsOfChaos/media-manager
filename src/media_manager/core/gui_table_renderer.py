from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_widget_specs import build_table_spec

TABLE_RENDERER_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_table_render_spec(table_state: Mapping[str, Any], *, table_id: str = "table") -> dict[str, object]:
    columns = _list(table_state.get("columns"))
    rows = _list(table_state.get("rows"))
    empty_state = _mapping(table_state.get("empty_state"))
    widget = build_table_spec(table_id, columns=[str(item) for item in columns], rows=[item for item in rows if isinstance(item, Mapping)], empty_state=empty_state)
    return {
        "schema_version": TABLE_RENDERER_SCHEMA_VERSION,
        "kind": "table_render_spec",
        "table_id": table_id,
        "widget": widget,
        "summary": {
            "column_count": len(columns),
            "row_count": len(rows),
            "empty": len(rows) == 0,
            "truncated": bool(table_state.get("truncated", False)),
        },
        "interactions": {
            "supports_search": True,
            "supports_sort": True,
            "supports_row_selection": True,
        },
    }


def table_columns_from_rows(rows: list[Mapping[str, Any]]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for key in row.keys():
            if str(key) not in columns:
                columns.append(str(key))
    return columns


__all__ = ["TABLE_RENDERER_SCHEMA_VERSION", "build_table_render_spec", "table_columns_from_rows"]
