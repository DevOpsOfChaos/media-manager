from __future__ import annotations
from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_OPERATOR_SHEET_SCHEMA_VERSION = "1.0"

def _m(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def build_qt_runtime_smoke_desktop_operator_sheet(start_plan: Mapping[str, Any]) -> dict[str, object]:
    command = _m(start_plan.get("command_line"))
    window = _m(start_plan.get("window_contract"))
    ready = bool(start_plan.get("ready_for_manual_start"))
    checks = [
        {"id": "read-command", "label": f"Review command: {command.get('display_command')}", "required": True},
        {"id": "confirm-local-only", "label": "Confirm local-only Runtime Smoke flow", "required": True},
        {"id": "confirm-window-title", "label": f"Expected window title: {window.get('title')}", "required": True},
        {"id": "confirm-active-page", "label": "Expected active page: runtime-smoke", "required": True},
        {"id": "confirm-no-auto-apply", "label": "Keine Apply-/Training-Aktion darf automatisch starten.", "required": True},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_OPERATOR_SHEET_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_operator_sheet",
        "ready": ready,
        "checks": checks,
        "summary": {"check_count": len(checks), "required_check_count": len(checks), "ready": ready, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_OPERATOR_SHEET_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_operator_sheet"]
