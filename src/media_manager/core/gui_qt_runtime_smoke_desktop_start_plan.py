from __future__ import annotations
from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_desktop_command_line import build_qt_runtime_smoke_desktop_command_line
from .gui_qt_runtime_smoke_desktop_environment import build_qt_runtime_smoke_desktop_environment
from .gui_qt_runtime_smoke_desktop_window_contract import build_qt_runtime_smoke_desktop_window_contract

QT_RUNTIME_SMOKE_DESKTOP_START_PLAN_SCHEMA_VERSION = "1.0"

def _m(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def build_qt_runtime_smoke_desktop_start_plan(rehearsal_bundle: Mapping[str, Any], *, language: str = "de", theme: str = "modern-dark") -> dict[str, object]:
    rehearsal_ready = bool(rehearsal_bundle.get("ready_for_manual_desktop_smoke") or rehearsal_bundle.get("ready"))
    environment = build_qt_runtime_smoke_desktop_environment(platform="Windows")
    command_line = build_qt_runtime_smoke_desktop_command_line(language=language, theme=theme)
    window = build_qt_runtime_smoke_desktop_window_contract()
    failed_required = int(_m(environment.get("summary")).get("failed_required_count") or 0)
    ready = rehearsal_ready and failed_required == 0
    steps = [
        {"id": "verify-rehearsal", "passed": rehearsal_ready, "required": True},
        {"id": "verify-environment", "passed": failed_required == 0, "required": True},
        {"id": "review-command-line", "passed": True, "required": True},
        {"id": "review-window-contract", "passed": True, "required": True},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_START_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_start_plan",
        "rehearsal_ready": rehearsal_ready,
        "environment": environment,
        "command_line": command_line,
        "window_contract": window,
        "ready_for_manual_start": ready,
        "steps": steps,
        "summary": {"step_count": len(steps), "failed_required_count": sum(1 for step in steps if step["required"] and not step["passed"]), "ready_for_manual_start": ready, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_START_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_start_plan"]
