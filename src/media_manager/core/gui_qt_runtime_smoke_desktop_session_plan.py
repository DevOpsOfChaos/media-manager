from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_SESSION_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_desktop_session_plan(
    rehearsal_plan: Mapping[str, Any],
    preflight: Mapping[str, Any],
) -> dict[str, object]:
    """Plan the manual desktop smoke session after headless preflight."""

    launch = _mapping(rehearsal_plan.get("launch"))
    preflight_summary = _mapping(preflight.get("summary"))
    command = " ".join([str(launch.get("entry_point") or "media-manager-gui"), *[str(arg) for arg in launch.get("args", []) if arg is not None]])
    ready = bool(preflight_summary.get("ready"))
    phases = [
        {"id": "start-app", "label": "Start the app manually", "manual": True, "ready": ready},
        {"id": "open-runtime-smoke", "label": "Open Runtime Smoke page", "manual": True, "ready": ready},
        {"id": "verify-navigation", "label": "Verify navigation and status slot", "manual": True, "ready": ready},
        {"id": "verify-no-auto-execution", "label": "Verify no command starts automatically", "manual": True, "ready": ready},
        {"id": "close-app", "label": "Close the app cleanly", "manual": True, "ready": ready},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_SESSION_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_session_plan",
        "page_id": rehearsal_plan.get("page_id"),
        "ready": ready,
        "display_command": command,
        "phases": phases,
        "summary": {
            "phase_count": len(phases),
            "manual_phase_count": sum(1 for phase in phases if phase["manual"]),
            "ready_phase_count": sum(1 for phase in phases if phase["ready"]),
            "ready_for_manual_session": ready,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_SESSION_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_session_plan"]
