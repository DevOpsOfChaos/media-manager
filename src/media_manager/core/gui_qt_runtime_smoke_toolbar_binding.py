from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_TOOLBAR_BINDING_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_toolbar_binding(shell_bundle: Mapping[str, Any]) -> dict[str, object]:
    """Normalize Runtime Smoke toolbar buttons for the desktop shell action row."""

    toolbar = _mapping(shell_bundle.get("toolbar"))
    buttons: list[dict[str, object]] = []
    for raw in _list(toolbar.get("buttons")):
        if not isinstance(raw, Mapping):
            continue
        buttons.append(
            {
                "id": raw.get("button_id") or str(raw.get("command_id") or "runtime-smoke.button").replace(".", "-"),
                "command_id": raw.get("command_id"),
                "label": raw.get("label"),
                "page_id": "runtime-smoke",
                "enabled": bool(raw.get("enabled")),
                "requires_confirmation": bool(raw.get("requires_confirmation")),
                "executes_immediately": False,
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_TOOLBAR_BINDING_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_toolbar_binding",
        "page_id": "runtime-smoke",
        "buttons": buttons,
        "summary": {
            "button_count": len(buttons),
            "enabled_button_count": sum(1 for button in buttons if button.get("enabled")),
            "confirmation_button_count": sum(1 for button in buttons if button.get("requires_confirmation")),
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


__all__ = ["QT_RUNTIME_SMOKE_TOOLBAR_BINDING_SCHEMA_VERSION", "build_qt_runtime_smoke_toolbar_binding"]
