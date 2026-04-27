from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_TOOLBAR_SCHEMA_VERSION = "1.0"
def _list(value: object) -> list[Any]: return value if isinstance(value, list) else []
def build_qt_runtime_smoke_shell_toolbar(command_surface: Mapping[str, Any]) -> dict[str, object]:
    buttons = []
    for command in _list(command_surface.get("commands")):
        if isinstance(command, Mapping) and command.get("id") in {"runtime-smoke.open", "runtime-smoke.refresh", "runtime-smoke.start-manual-smoke"}:
            buttons.append({"button_id": str(command.get("id")).replace(".", "-"), "command_id": command.get("id"), "label": command.get("label"), "enabled": bool(command.get("enabled")), "requires_confirmation": bool(command.get("requires_confirmation")), "executes_immediately": False})
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_TOOLBAR_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_toolbar", "page_id": command_surface.get("page_id"), "buttons": buttons, "summary": {"button_count": len(buttons), "enabled_button_count": sum(1 for b in buttons if b["enabled"]), "confirmation_button_count": sum(1 for b in buttons if b["requires_confirmation"]), "immediate_execution_count": 0}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_TOOLBAR_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_toolbar"]
