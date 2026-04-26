from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

COMPONENT_SCHEMA_VERSION = "1.0"


def _text(value: object, fallback: str = "") -> str:
    return str(value) if value is not None and str(value) else fallback


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_action_button(
    action_id: str,
    label: str,
    *,
    variant: str = "secondary",
    enabled: bool = True,
    icon: str | None = None,
    description: str = "",
    risk_level: str = "safe",
    command_preview: Iterable[str] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": COMPONENT_SCHEMA_VERSION,
        "component": "action_button",
        "id": action_id,
        "label": label,
        "variant": variant,
        "enabled": bool(enabled),
        "icon": icon,
        "description": description,
        "risk_level": risk_level,
        "command_preview": list(command_preview or ()),
    }


def build_metric_tile(
    tile_id: str,
    label: str,
    value: object,
    *,
    helper: str = "",
    trend: str | None = None,
    tone: str = "neutral",
) -> dict[str, object]:
    return {
        "schema_version": COMPONENT_SCHEMA_VERSION,
        "component": "metric_tile",
        "id": tile_id,
        "label": label,
        "value": value,
        "helper": helper,
        "trend": trend,
        "tone": tone,
    }


def build_card(
    card_id: str,
    title: str,
    *,
    subtitle: str = "",
    icon: str | None = None,
    tone: str = "neutral",
    metrics: Mapping[str, Any] | None = None,
    actions: Iterable[Mapping[str, Any]] = (),
    body: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    return {
        "schema_version": COMPONENT_SCHEMA_VERSION,
        "component": "card",
        "id": card_id,
        "title": title,
        "subtitle": subtitle,
        "icon": icon,
        "tone": tone,
        "metrics": dict(metrics or {}),
        "actions": [dict(action) for action in actions],
        "body": dict(body or {}),
    }


def build_table_model(
    table_id: str,
    columns: Iterable[str],
    rows: Iterable[Mapping[str, Any]],
    *,
    empty_state: str = "",
    row_actions: Iterable[Mapping[str, Any]] = (),
) -> dict[str, object]:
    row_list = [dict(row) for row in rows]
    return {
        "schema_version": COMPONENT_SCHEMA_VERSION,
        "component": "table",
        "id": table_id,
        "columns": list(columns),
        "rows": row_list,
        "row_count": len(row_list),
        "empty_state": empty_state if not row_list else None,
        "row_actions": [dict(action) for action in row_actions],
    }


def build_status_badge(status: object, *, tone: str | None = None) -> dict[str, object]:
    value = _text(status, "unknown")
    resolved_tone = tone
    if resolved_tone is None:
        resolved_tone = {
            "ok": "success",
            "ready_to_apply": "success",
            "completed": "success",
            "needs_review": "warning",
            "needs_name": "warning",
            "error": "danger",
            "failed": "danger",
            "blocked": "danger",
        }.get(value, "neutral")
    return {
        "schema_version": COMPONENT_SCHEMA_VERSION,
        "component": "status_badge",
        "status": value,
        "tone": resolved_tone,
    }


def normalize_component_tree(value: Mapping[str, Any]) -> dict[str, object]:
    """Return a shallow normalized component payload for GUI renderers."""
    payload = dict(value)
    payload.setdefault("schema_version", COMPONENT_SCHEMA_VERSION)
    payload.setdefault("component", "unknown")
    return payload


__all__ = [
    "COMPONENT_SCHEMA_VERSION",
    "build_action_button",
    "build_card",
    "build_metric_tile",
    "build_status_badge",
    "build_table_model",
    "normalize_component_tree",
]
