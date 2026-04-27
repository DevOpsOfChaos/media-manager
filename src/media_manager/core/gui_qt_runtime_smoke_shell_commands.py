from __future__ import annotations
from collections.abc import Mapping
from typing import Any
QT_RUNTIME_SMOKE_SHELL_COMMANDS_SCHEMA_VERSION = "1.0"
def _command(command_id: str, label: str, *, enabled: bool, requires_confirmation: bool = False) -> dict[str, object]: return {"id": command_id, "label": label, "enabled": bool(enabled), "requires_confirmation": bool(requires_confirmation), "execute_policy": "manual_confirm" if requires_confirmation else "deferred", "executes_immediately": False}
def build_qt_runtime_smoke_shell_commands(shell_registration: Mapping[str, Any]) -> dict[str, object]:
    enabled = bool(shell_registration.get("enabled"))
    commands = [_command("runtime-smoke.open", "Open Runtime Smoke page", enabled=enabled), _command("runtime-smoke.refresh", "Refresh Runtime Smoke state", enabled=True), _command("runtime-smoke.export-metadata", "Export Runtime Smoke metadata", enabled=enabled), _command("runtime-smoke.start-manual-smoke", "Start manual Qt smoke", enabled=enabled, requires_confirmation=True)]
    return {"schema_version": QT_RUNTIME_SMOKE_SHELL_COMMANDS_SCHEMA_VERSION, "kind": "qt_runtime_smoke_shell_commands", "page_id": shell_registration.get("page_id"), "commands": commands, "summary": {"command_count": len(commands), "enabled_command_count": sum(1 for c in commands if c["enabled"]), "confirmation_command_count": sum(1 for c in commands if c["requires_confirmation"]), "immediate_execution_count": 0}, "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True}}
__all__ = ["QT_RUNTIME_SMOKE_SHELL_COMMANDS_SCHEMA_VERSION", "build_qt_runtime_smoke_shell_commands"]
