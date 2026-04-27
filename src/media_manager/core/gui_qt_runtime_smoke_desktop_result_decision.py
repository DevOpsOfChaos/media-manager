from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_DECISION_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_result_decision(summary: Mapping[str, Any], audit: Mapping[str, Any]) -> dict[str, object]:
    if audit.get("valid") is not True:
        decision = "blocked"
        severity = "error"
        next_step = "Fix result validation or privacy issues before accepting the desktop smoke."
    elif summary.get("passed") is True:
        decision = "accepted"
        severity = "success"
        next_step = "Desktop smoke can be marked accepted."
    elif int(summary.get("missing_required_count") or 0) > 0:
        decision = "needs_results"
        severity = "warning"
        next_step = "Complete missing required desktop smoke checks."
    else:
        decision = "failed"
        severity = "error"
        next_step = "Review failed required desktop smoke checks."
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_DECISION_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_decision",
        "decision": decision,
        "severity": severity,
        "recommended_next_step": next_step,
        "requires_user_confirmation": True,
        "executes_immediately": False,
        "opens_window": False,
        "local_only": True,
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_DECISION_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_result_decision"]
