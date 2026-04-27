from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_INTEGRATION_REPORT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_runtime_smoke_integration_report(
    matrix: Mapping[str, Any],
    gate: Mapping[str, Any],
    checklist: Mapping[str, Any],
    risk: Mapping[str, Any],
) -> dict[str, object]:
    """Build an integration report for Runtime Smoke shell readiness."""

    matrix_summary = _mapping(matrix.get("summary"))
    checklist_summary = _mapping(checklist.get("summary"))
    ready = bool(gate.get("ready")) and bool(checklist_summary.get("ready")) and risk.get("level") == "low"
    return {
        "schema_version": QT_RUNTIME_SMOKE_INTEGRATION_REPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_integration_report",
        "ready": ready,
        "decision": "proceed" if ready else "hold",
        "matrix": dict(matrix),
        "gate": dict(gate),
        "checklist": dict(checklist),
        "risk": dict(risk),
        "summary": {
            "ready": ready,
            "matrix_row_count": matrix_summary.get("row_count", 0),
            "problem_count": gate.get("problem_count", 0),
            "failed_required_check_count": checklist_summary.get("failed_required_count", 0),
            "risk_level": risk.get("level"),
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


def summarize_qt_runtime_smoke_integration_report(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    return "\n".join(
        [
            "Qt runtime smoke integration report",
            f"  Ready: {report.get('ready')}",
            f"  Decision: {report.get('decision')}",
            f"  Problems: {summary.get('problem_count', 0)}",
            f"  Failed required checks: {summary.get('failed_required_check_count', 0)}",
            f"  Risk: {summary.get('risk_level')}",
            f"  Opens window: {summary.get('opens_window')}",
            f"  Executes commands: {summary.get('executes_commands')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_SMOKE_INTEGRATION_REPORT_SCHEMA_VERSION",
    "build_qt_runtime_smoke_integration_report",
    "summarize_qt_runtime_smoke_integration_report",
]
