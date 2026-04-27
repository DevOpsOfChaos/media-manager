from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_PREFLIGHT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_desktop_preflight(rehearsal_plan: Mapping[str, Any]) -> dict[str, object]:
    """Build a headless preflight checklist for the manual desktop rehearsal."""

    summary = _mapping(rehearsal_plan.get("summary"))
    launch = _mapping(rehearsal_plan.get("launch"))
    checks = [
        {"id": "plan-ready", "label": "Rehearsal plan is ready", "passed": bool(rehearsal_plan.get("ready")), "required": True},
        {"id": "wiring-clean", "label": "No wiring problems", "passed": int(summary.get("wiring_problem_count") or 0) == 0, "required": True},
        {"id": "manual-only-launch", "label": "Launch is manual-only", "passed": bool(launch.get("manual_only")), "required": True},
        {"id": "no-headless-window", "label": "Preflight does not open a window", "passed": launch.get("opens_window_during_plan") is False, "required": True},
        {"id": "no-command-execution", "label": "Preflight does not execute commands", "passed": launch.get("executes_immediately") is False, "required": True},
        {"id": "local-only", "label": "Runtime Smoke remains local-only", "passed": summary.get("local_only") is True, "required": True},
    ]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_PREFLIGHT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_preflight",
        "page_id": rehearsal_plan.get("page_id"),
        "checks": checks,
        "summary": {
            "check_count": len(checks),
            "required_check_count": sum(1 for check in checks if check["required"]),
            "passed_count": sum(1 for check in checks if check["passed"]),
            "failed_required_count": sum(1 for check in checks if check["required"] and not check["passed"]),
            "ready": all(check["passed"] for check in checks if check["required"]),
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_PREFLIGHT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_preflight"]
