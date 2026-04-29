from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_COMMAND_PALETTE_BINDING_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_command_palette_binding(shell_bundle: Mapping[str, Any]) -> dict[str, object]:
    """Expose Runtime Smoke shell commands as deferred command-palette items."""

    command_surface = _mapping(shell_bundle.get("commands"))
    items: list[dict[str, object]] = []
    for raw in _list(command_surface.get("commands")):
        if not isinstance(raw, Mapping):
            continue
        command_id = str(raw.get("id") or "runtime-smoke.command")
        items.append(
            {
                "id": command_id,
                "label": raw.get("label") or command_id.replace("-", " ").replace(".", " ").title(),
                "category": "Runtime Smoke",
                "page_id": "runtime-smoke",
                "enabled": bool(raw.get("enabled")),
                "requires_confirmation": bool(raw.get("requires_confirmation")),
                "executes_immediately": False,
                "intent": {"type": "runtime_smoke_command", "command_id": command_id},
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_COMMAND_PALETTE_BINDING_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_command_palette_binding",
        "page_id": "runtime-smoke",
        "items": items,
        "summary": {
            "item_count": len(items),
            "enabled_item_count": sum(1 for item in items if item.get("enabled")),
            "confirmation_item_count": sum(1 for item in items if item.get("requires_confirmation")),
            "immediate_execution_count": 0,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = [
    "QT_RUNTIME_SMOKE_COMMAND_PALETTE_BINDING_SCHEMA_VERSION",
    "build_qt_runtime_smoke_command_palette_binding",
]
