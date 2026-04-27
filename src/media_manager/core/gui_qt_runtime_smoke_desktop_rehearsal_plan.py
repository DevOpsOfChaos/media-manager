from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_PLAN_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_desktop_rehearsal_plan(
    wiring_bundle: Mapping[str, Any],
    *,
    language: str = "en",
    theme: str = "modern-dark",
) -> dict[str, object]:
    """Plan a desktop runtime smoke rehearsal without importing PySide6 or opening a window."""

    summary = _mapping(wiring_bundle.get("summary"))
    ready = bool(wiring_bundle.get("ready_for_guarded_shell_wiring"))
    steps = [
        {"id": "verify-wiring-bundle", "label": "Verify guarded shell wiring bundle", "ready": ready},
        {"id": "verify-page-loader", "label": "Verify lazy page loader contract", "ready": ready},
        {"id": "verify-command-dispatch", "label": "Verify deferred command dispatch", "ready": ready},
        {"id": "prepare-manual-launch", "label": "Prepare manual Qt launch command", "ready": ready},
        {"id": "prepare-rollback", "label": "Prepare rollback plan", "ready": ready},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_PLAN_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_rehearsal_plan",
        "page_id": "runtime-smoke",
        "language": "de" if language == "de" else "en",
        "theme": str(theme or "modern-dark"),
        "ready": ready,
        "wiring_bundle": dict(wiring_bundle),
        "steps": steps,
        "launch": {
            "entry_point": "media-manager-gui",
            "args": ["--language", "de" if language == "de" else "en", "--theme", str(theme or "modern-dark"), "--active-page", "runtime-smoke"],
            "manual_only": True,
            "executes_immediately": False,
            "opens_window_during_plan": False,
        },
        "summary": {
            "step_count": len(steps),
            "ready_step_count": sum(1 for step in steps if step["ready"]),
            "wiring_problem_count": int(summary.get("problem_count") or 0),
            "ready_for_manual_desktop_rehearsal": ready,
            "local_only": True,
            "opens_window": False,
            "executes_commands": False,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_PLAN_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_rehearsal_plan"]
