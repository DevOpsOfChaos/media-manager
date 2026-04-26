from __future__ import annotations

from collections.abc import Mapping
from typing import Any

COMMAND_PALETTE_PLAN_SCHEMA_VERSION = "1.0"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any, default: str = "") -> str:
    return str(value) if value is not None else default


def build_qt_command_palette_plan(shell_model: Mapping[str, Any], *, query: str = "") -> dict[str, Any]:
    palette = _as_mapping(shell_model.get("command_palette"))
    actions = [item for item in _as_list(palette.get("items", palette.get("commands"))) if isinstance(item, Mapping)]
    normalized_query = query.strip().casefold()
    filtered = []
    for action in actions:
        haystack = " ".join(str(action.get(key, "")) for key in ("id", "label", "description", "page_id")).casefold()
        if not normalized_query or normalized_query in haystack:
            filtered.append(action)
    rows = [
        {
            "id": _text(action.get("id"), f"action-{index + 1}"),
            "label": action.get("label") or action.get("title") or action.get("id"),
            "description": action.get("description", ""),
            "page_id": action.get("page_id"),
            "enabled": bool(action.get("enabled", True)),
            "requires_confirmation": bool(action.get("requires_confirmation", False)),
        }
        for index, action in enumerate(filtered[:30])
    ]
    return {
        "schema_version": COMMAND_PALETTE_PLAN_SCHEMA_VERSION,
        "kind": "qt_command_palette_plan",
        "query": query,
        "row_count": len(rows),
        "truncated": len(filtered) > len(rows),
        "rows": rows,
        "shortcuts": ["Ctrl+K", "Ctrl+P"],
        "empty_state": None if rows else "No command matches the current search.",
    }


def command_palette_row_to_intent(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": COMMAND_PALETTE_PLAN_SCHEMA_VERSION,
        "kind": "command_palette_intent",
        "action_id": row.get("id"),
        "page_id": row.get("page_id"),
        "enabled": bool(row.get("enabled", True)),
        "requires_confirmation": bool(row.get("requires_confirmation", False)),
        "executes_immediately": False,
    }


__all__ = ["COMMAND_PALETTE_PLAN_SCHEMA_VERSION", "build_qt_command_palette_plan", "command_palette_row_to_intent"]
