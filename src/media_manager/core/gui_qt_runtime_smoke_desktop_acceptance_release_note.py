from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_RELEASE_NOTE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_release_note(gate: Mapping[str, Any], quality: Mapping[str, Any]) -> dict[str, object]:
    ready = bool(gate.get("ready"))
    text = (
        "Runtime Smoke desktop acceptance is ready for guarded manual Qt wiring."
        if ready
        else "Runtime Smoke desktop acceptance is blocked; resolve desktop smoke issues before wiring."
    )
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_RELEASE_NOTE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_release_note",
        "ready": ready,
        "text": text,
        "quality_level": quality.get("level"),
        "summary": {
            "ready": ready,
            "quality_level": quality.get("level"),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_RELEASE_NOTE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_release_note"]
