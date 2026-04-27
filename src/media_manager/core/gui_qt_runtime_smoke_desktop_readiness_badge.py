from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_READINESS_BADGE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_readiness_badge(audit: Mapping[str, Any]) -> dict[str, object]:
    valid = bool(audit.get("valid"))
    problem_count = int(audit.get("problem_count") or 0)
    if valid:
        state, severity, text = "ready", "success", "Ready for manual desktop smoke"
    elif problem_count <= 2:
        state, severity, text = "blocked", "warning", "Desktop smoke needs attention"
    else:
        state, severity, text = "blocked", "error", "Desktop smoke blocked"
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_READINESS_BADGE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_readiness_badge",
        "state": state,
        "severity": severity,
        "text": text,
        "problem_count": problem_count,
        "ready": valid,
        "opens_window": False,
        "executes_commands": False,
        "local_only": True,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_READINESS_BADGE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_readiness_badge"]
