from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

FILTER_BAR_SCHEMA_VERSION = "1.0"


def build_filter_option(option_id: str, label: str, *, active: bool = False, count: int | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"id": str(option_id), "label": str(label), "active": bool(active)}
    if count is not None:
        payload["count"] = max(0, int(count))
    return payload


def build_filter_bar(
    *,
    filter_id: str,
    options: Iterable[Mapping[str, Any]],
    selected_id: object = "all",
    label: str = "Filter",
) -> dict[str, object]:
    selected = str(selected_id or "all")
    normalized_options = []
    for raw in options:
        option = dict(raw)
        option_id = str(option.get("id") or "")
        option["active"] = option_id == selected
        normalized_options.append(option)
    if not any(item.get("active") for item in normalized_options) and normalized_options:
        normalized_options[0]["active"] = True
        selected = str(normalized_options[0].get("id"))
    return {
        "schema_version": FILTER_BAR_SCHEMA_VERSION,
        "kind": "filter_bar",
        "filter_id": filter_id,
        "label": label,
        "selected_id": selected,
        "options": normalized_options,
        "option_count": len(normalized_options),
    }


def apply_status_filter(rows: Iterable[Mapping[str, Any]], *, selected_id: object = "all", status_key: str = "status") -> list[dict[str, Any]]:
    selected = str(selected_id or "all")
    row_list = [dict(row) for row in rows]
    if selected in {"", "all"}:
        return row_list
    return [row for row in row_list if str(row.get(status_key)) == selected]


def build_status_filter_bar(rows: Iterable[Mapping[str, Any]], *, selected_id: object = "all", status_key: str = "status") -> dict[str, object]:
    counts: dict[str, int] = {"all": 0}
    for row in rows:
        counts["all"] += 1
        status = str(row.get(status_key) or "unknown")
        counts[status] = counts.get(status, 0) + 1
    options = [build_filter_option("all", "All", count=counts["all"])]
    for status, count in sorted((key, value) for key, value in counts.items() if key != "all"):
        options.append(build_filter_option(status, status.replace("_", " ").title(), count=count))
    return build_filter_bar(filter_id=status_key, options=options, selected_id=selected_id)


__all__ = [
    "FILTER_BAR_SCHEMA_VERSION",
    "apply_status_filter",
    "build_filter_bar",
    "build_filter_option",
    "build_status_filter_bar",
]
