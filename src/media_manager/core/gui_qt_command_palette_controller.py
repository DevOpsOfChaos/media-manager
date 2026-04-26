from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

COMMAND_PALETTE_CONTROLLER_SCHEMA_VERSION = "1.0"


def _text(value: object) -> str:
    return str(value) if value is not None else ""


def filter_palette_commands(commands: Sequence[Mapping[str, Any]], query: str = "") -> list[dict[str, object]]:
    normalized = query.strip().casefold()
    rows: list[dict[str, object]] = []
    for command in commands:
        haystack = " ".join(_text(command.get(key)) for key in ("id", "label", "description", "page_id")).casefold()
        if normalized and normalized not in haystack:
            continue
        rows.append(
            {
                "id": _text(command.get("id")),
                "label": _text(command.get("label") or command.get("id")),
                "description": _text(command.get("description")),
                "page_id": command.get("page_id"),
                "enabled": bool(command.get("enabled", True)),
                "intent": command.get("intent") or {"type": "navigate", "page_id": command.get("page_id")},
            }
        )
    return rows


def build_qt_command_palette_controller(
    commands: Sequence[Mapping[str, Any]],
    *,
    query: str = "",
    selected_index: int = 0,
) -> dict[str, object]:
    rows = filter_palette_commands(commands, query=query)
    safe_index = min(max(0, int(selected_index)), max(0, len(rows) - 1)) if rows else None
    return {
        "schema_version": COMMAND_PALETTE_CONTROLLER_SCHEMA_VERSION,
        "kind": "qt_command_palette_controller",
        "query": query,
        "row_count": len(rows),
        "selected_index": safe_index,
        "selected_command": rows[safe_index] if safe_index is not None else None,
        "rows": rows,
        "empty": not rows,
    }


__all__ = ["COMMAND_PALETTE_CONTROLLER_SCHEMA_VERSION", "build_qt_command_palette_controller", "filter_palette_commands"]
