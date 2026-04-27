from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_INTEGRATION_RISK_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_integration_risk(gate: Mapping[str, Any], checklist: Mapping[str, Any]) -> dict[str, object]:
    """Summarize remaining integration risk for Runtime Smoke."""

    failed = int(checklist.get("summary", {}).get("failed_required_count", 0)) if isinstance(checklist.get("summary"), Mapping) else 0
    problem_count = int(gate.get("problem_count") or 0)
    if problem_count == 0 and failed == 0:
        level = "low"
        recommendation = "Proceed with guarded shell wiring in the next block."
    elif problem_count <= 2:
        level = "medium"
        recommendation = "Fix the listed integration blockers before shell wiring."
    else:
        level = "high"
        recommendation = "Do not integrate into the shell yet."
    return {
        "schema_version": QT_RUNTIME_SMOKE_INTEGRATION_RISK_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_integration_risk",
        "level": level,
        "recommendation": recommendation,
        "problem_count": problem_count,
        "failed_required_check_count": failed,
        "allows_next_shell_wiring": level == "low",
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


__all__ = ["QT_RUNTIME_SMOKE_INTEGRATION_RISK_SCHEMA_VERSION", "build_qt_runtime_smoke_integration_risk"]
