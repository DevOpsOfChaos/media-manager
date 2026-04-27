from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_REPORT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_desktop_rehearsal_report(
    rehearsal_plan: Mapping[str, Any],
    preflight: Mapping[str, Any],
    session_plan: Mapping[str, Any],
    manual_steps: Mapping[str, Any],
    failure_hints: Mapping[str, Any],
    launch_notes: Mapping[str, Any],
    audit: Mapping[str, Any],
    readiness_badge: Mapping[str, Any],
) -> dict[str, object]:
    ready = bool(audit.get("valid")) and bool(readiness_badge.get("ready"))
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_REPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_rehearsal_report",
        "ready": ready,
        "decision": "ready_for_manual_desktop_smoke" if ready else "blocked",
        "rehearsal_plan": dict(rehearsal_plan),
        "preflight": dict(preflight),
        "session_plan": dict(session_plan),
        "manual_steps": dict(manual_steps),
        "failure_hints": dict(failure_hints),
        "launch_notes": dict(launch_notes),
        "audit": dict(audit),
        "readiness_badge": dict(readiness_badge),
        "summary": {
            "ready": ready,
            "preflight_failed_required_count": _mapping(preflight.get("summary")).get("failed_required_count", 0),
            "manual_step_count": _mapping(manual_steps.get("summary")).get("manual_step_count", 0),
            "hint_count": _mapping(failure_hints.get("summary")).get("hint_count", 0),
            "audit_problem_count": audit.get("problem_count", 0),
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


def summarize_qt_runtime_smoke_desktop_rehearsal_report(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    return "\n".join(
        [
            "Qt runtime smoke desktop rehearsal",
            f"  Ready: {report.get('ready')}",
            f"  Decision: {report.get('decision')}",
            f"  Manual steps: {summary.get('manual_step_count', 0)}",
            f"  Hints: {summary.get('hint_count', 0)}",
            f"  Audit problems: {summary.get('audit_problem_count', 0)}",
            f"  Opens window: {summary.get('opens_window')}",
            f"  Executes commands: {summary.get('executes_commands')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_REPORT_SCHEMA_VERSION",
    "build_qt_runtime_smoke_desktop_rehearsal_report",
    "summarize_qt_runtime_smoke_desktop_rehearsal_report",
]
