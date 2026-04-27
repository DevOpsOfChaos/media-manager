from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_MANUAL_STEPS_SCHEMA_VERSION = "1.0"


def _list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def build_qt_runtime_smoke_desktop_manual_steps(session_plan: Mapping[str, Any], *, language: str = "en") -> dict[str, object]:
    """Build a bilingual manual checklist for a later visible Qt smoke run."""

    lang = "de" if language == "de" else "en"
    labels = {
        "start-app": ("Start app manually", "App manuell starten"),
        "open-runtime-smoke": ("Open Runtime Smoke page", "Runtime-Smoke-Seite öffnen"),
        "verify-navigation": ("Navigation and status slot are visible", "Navigation und Statusbereich sind sichtbar"),
        "verify-no-auto-execution": ("No command executes automatically", "Kein Command startet automatisch"),
        "close-app": ("Close app cleanly", "App sauber schließen"),
    }
    steps = []
    for index, phase in enumerate(_list(session_plan.get("phases"))):
        if not isinstance(phase, Mapping):
            continue
        phase_id = str(phase.get("id") or f"phase-{index + 1}")
        en, de = labels.get(phase_id, (str(phase.get("label") or phase_id), str(phase.get("label") or phase_id)))
        steps.append(
            {
                "id": phase_id,
                "order": index + 1,
                "label": de if lang == "de" else en,
                "required": True,
                "expected_result": "pass",
                "manual": True,
            }
        )
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_MANUAL_STEPS_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_manual_steps",
        "language": lang,
        "page_id": session_plan.get("page_id"),
        "steps": steps,
        "summary": {
            "step_count": len(steps),
            "required_step_count": sum(1 for step in steps if step["required"]),
            "manual_step_count": sum(1 for step in steps if step["manual"]),
            "ready": bool(session_plan.get("ready")),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_MANUAL_STEPS_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_manual_steps"]
