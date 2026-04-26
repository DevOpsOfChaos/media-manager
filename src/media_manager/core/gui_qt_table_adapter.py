from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

TABLE_ADAPTER_SCHEMA_VERSION = "1.0"


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, Mapping):
        for key in ("label", "value", "path", "status", "id"):
            if value.get(key) is not None:
                return str(value[key])
        return ""
    return str(value)


def _as_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def infer_table_columns(rows: Sequence[Mapping[str, Any]], *, preferred: Sequence[str] = ()) -> list[str]:
    seen: list[str] = []
    for item in preferred:
        if item and item not in seen:
            seen.append(str(item))
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.append(str(key))
    return seen


def build_qt_table_adapter(
    *,
    rows: Sequence[Mapping[str, Any]],
    columns: Sequence[str] | None = None,
    max_rows: int = 500,
) -> dict[str, object]:
    selected_columns = list(columns or infer_table_columns(rows))
    visible_rows = list(rows)[: max(0, int(max_rows))]
    matrix = [[_text(row.get(column)) for column in selected_columns] for row in visible_rows]
    column_widths = {
        column: min(360, max(80, max([len(column), *[len(row[index]) for row in matrix]] or [len(column)]) * 9))
        for index, column in enumerate(selected_columns)
    }
    return {
        "schema_version": TABLE_ADAPTER_SCHEMA_VERSION,
        "kind": "qt_table_adapter",
        "columns": selected_columns,
        "row_count": len(rows),
        "visible_row_count": len(visible_rows),
        "truncated": len(rows) > len(visible_rows),
        "matrix": matrix,
        "column_widths": column_widths,
        "selection_behavior": "rows",
        "alternating_row_colors": True,
    }


def table_adapter_summary(adapter: Mapping[str, Any]) -> str:
    return f"{adapter.get('visible_row_count', 0)}/{adapter.get('row_count', 0)} rows, {len(_as_list(adapter.get('columns')))} columns"


__all__ = ["TABLE_ADAPTER_SCHEMA_VERSION", "build_qt_table_adapter", "infer_table_columns", "table_adapter_summary"]
