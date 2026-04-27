from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_LAUNCH_NOTES_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_launch_notes(session_plan: Mapping[str, Any], manual_steps: Mapping[str, Any]) -> dict[str, object]:
    """Build local launch notes for a future manual desktop smoke run."""

    command = str(session_plan.get("display_command") or "media-manager-gui --active-page runtime-smoke")
    ready = bool(session_plan.get("ready")) and bool(manual_steps.get("summary", {}).get("ready")) if isinstance(manual_steps.get("summary"), Mapping) else bool(session_plan.get("ready"))
    notes = [
        "Install GUI extras only when you are ready for a visible Qt smoke run.",
        "Start the command manually; this plan must not execute it.",
        "Verify Runtime Smoke page, navigation, status slot, and no automatic destructive action.",
        "Keep People Review data local-only.",
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_LAUNCH_NOTES_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_launch_notes",
        "ready": ready,
        "display_command": command,
        "install_hint": 'python -m pip install -e ".[gui]"',
        "notes": notes,
        "summary": {
            "note_count": len(notes),
            "ready": ready,
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_LAUNCH_NOTES_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_launch_notes"]
