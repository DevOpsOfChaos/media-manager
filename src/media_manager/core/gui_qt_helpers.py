from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

QT_HELPER_SCHEMA_VERSION = "1.0"


def as_text(value: object, default: str = "") -> str:
    if value is None:
        return default
    text = str(value)
    return text if text else default


def as_mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def as_list(value: object) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def clamp_int(value: object, *, minimum: int, maximum: int, default: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def compact_metrics(metrics: Mapping[str, Any] | None, *, limit: int = 8) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for key, value in list(dict(metrics or {}).items())[: max(0, limit)]:
        result.append({"key": str(key), "label": str(key).replace("_", " ").title(), "value": value})
    return result


def widget(widget_type: str, *, widget_id: str, **payload: Any) -> dict[str, object]:
    data: dict[str, object] = {
        "schema_version": QT_HELPER_SCHEMA_VERSION,
        "widget_type": widget_type,
        "widget_id": widget_id,
    }
    data.update(payload)
    return data


def summarize_widgets(widgets: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    by_type: dict[str, int] = {}
    for item in widgets:
        widget_type = as_text(item.get("widget_type"), "unknown")
        by_type[widget_type] = by_type.get(widget_type, 0) + 1
    return {"widget_count": len(widgets), "widget_type_summary": dict(sorted(by_type.items()))}


__all__ = [
    "QT_HELPER_SCHEMA_VERSION",
    "as_list",
    "as_mapping",
    "as_text",
    "clamp_int",
    "compact_metrics",
    "summarize_widgets",
    "widget",
]
