from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

TABLE_STATE_SCHEMA_VERSION = "1.0"


def _text(value: object) -> str:
    return str(value) if value is not None else ""


def filter_table_rows(rows: Iterable[Mapping[str, Any]], *, query: str = "", status_filter: str = "all") -> list[dict[str, object]]:
    normalized_query = query.strip().casefold()
    normalized_status = status_filter.strip().casefold() or "all"
    result: list[dict[str, object]] = []
    for row in rows:
        payload = dict(row)
        text = " ".join(_text(value) for value in payload.values()).casefold()
        if normalized_query and normalized_query not in text:
            continue
        if normalized_status != "all":
            status = _text(payload.get("status") or payload.get("decision_status") or payload.get("valid")).casefold()
            if normalized_status not in status:
                continue
        result.append(payload)
    return result


def sort_table_rows(rows: Iterable[Mapping[str, Any]], *, sort_key: str = "", descending: bool = False) -> list[dict[str, object]]:
    items = [dict(row) for row in rows]
    if not sort_key:
        return items
    return sorted(items, key=lambda row: _text(row.get(sort_key)).casefold(), reverse=descending)


def build_table_state(
    *,
    table_id: str,
    columns: Iterable[str],
    rows: Iterable[Mapping[str, Any]],
    query: str = "",
    status_filter: str = "all",
    sort_key: str = "",
    descending: bool = False,
    limit: int = 200,
) -> dict[str, object]:
    filtered = filter_table_rows(rows, query=query, status_filter=status_filter)
    sorted_rows = sort_table_rows(filtered, sort_key=sort_key, descending=descending)
    limited = sorted_rows[: max(0, limit)]
    return {
        "schema_version": TABLE_STATE_SCHEMA_VERSION,
        "table_id": table_id,
        "columns": list(columns),
        "query": query,
        "status_filter": status_filter,
        "sort_key": sort_key,
        "descending": descending,
        "total_row_count": len(list(rows)) if not isinstance(rows, list) else len(rows),
        "filtered_row_count": len(filtered),
        "returned_row_count": len(limited),
        "truncated": len(sorted_rows) > len(limited),
        "rows": limited,
    }


__all__ = ["TABLE_STATE_SCHEMA_VERSION", "build_table_state", "filter_table_rows", "sort_table_rows"]
