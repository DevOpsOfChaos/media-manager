from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

SEARCH_SCHEMA_VERSION = "1.0"


def normalize_query(query: object) -> str:
    return " ".join(str(query or "").strip().split()).casefold()


def build_search_state(
    *,
    query: object = "",
    placeholder: str = "Search...",
    fields: Iterable[str] = (),
    enabled: bool = True,
) -> dict[str, object]:
    normalized = normalize_query(query)
    return {
        "schema_version": SEARCH_SCHEMA_VERSION,
        "kind": "search_state",
        "query": str(query or "").strip(),
        "normalized_query": normalized,
        "placeholder": placeholder,
        "fields": [str(field) for field in fields],
        "enabled": bool(enabled),
        "active": bool(normalized),
    }


def _value_matches(value: object, query: str) -> bool:
    if value is None:
        return False
    if isinstance(value, Mapping):
        return any(_value_matches(item, query) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_value_matches(item, query) for item in value)
    return query in str(value).casefold()


def apply_search(rows: Iterable[Mapping[str, Any]], *, query: object, fields: Iterable[str] = ()) -> list[dict[str, Any]]:
    normalized = normalize_query(query)
    row_list = [dict(row) for row in rows]
    if not normalized:
        return row_list
    field_list = [str(field) for field in fields if str(field).strip()]
    result: list[dict[str, Any]] = []
    for row in row_list:
        values = [row.get(field) for field in field_list] if field_list else list(row.values())
        if any(_value_matches(value, normalized) for value in values):
            result.append(row)
    return result


def summarize_search(*, original_count: int, returned_count: int, query: object) -> dict[str, object]:
    normalized = normalize_query(query)
    return {
        "schema_version": SEARCH_SCHEMA_VERSION,
        "query": str(query or "").strip(),
        "active": bool(normalized),
        "original_count": max(0, int(original_count)),
        "returned_count": max(0, int(returned_count)),
        "filtered_count": max(0, int(original_count) - int(returned_count)),
    }


__all__ = ["SEARCH_SCHEMA_VERSION", "apply_search", "build_search_state", "normalize_query", "summarize_search"]
