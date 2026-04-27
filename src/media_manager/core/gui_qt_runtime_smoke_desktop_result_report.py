from __future__ import annotations

from collections.abc import Mapping
from typing import Any

QT_RUNTIME_SMOKE_DESKTOP_RESULT_REPORT_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_result_report(
    validation: Mapping[str, Any],
    summary: Mapping[str, Any],
    audit: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, object]:
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_REPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_report",
        "accepted": decision.get("decision") == "accepted",
        "validation": dict(validation),
        "result_summary": dict(summary),
        "audit": dict(audit),
        "decision": dict(decision),
        "summary": {
            "accepted": decision.get("decision") == "accepted",
            "decision": decision.get("decision"),
            "result_count": summary.get("result_count", 0),
            "failed_required_count": summary.get("failed_required_count", 0),
            "missing_required_count": summary.get("missing_required_count", 0),
            "problem_count": audit.get("problem_count", 0),
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


def summarize_qt_runtime_smoke_desktop_result_report(report: Mapping[str, Any]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), Mapping) else {}
    return "\n".join(
        [
            "Qt runtime smoke desktop result report",
            f"  Accepted: {report.get('accepted')}",
            f"  Decision: {summary.get('decision')}",
            f"  Results: {summary.get('result_count', 0)}",
            f"  Failed required: {summary.get('failed_required_count', 0)}",
            f"  Missing required: {summary.get('missing_required_count', 0)}",
            f"  Opens window: {summary.get('opens_window')}",
            f"  Executes commands: {summary.get('executes_commands')}",
        ]
    )


__all__ = [
    "QT_RUNTIME_SMOKE_DESKTOP_RESULT_REPORT_SCHEMA_VERSION",
    "build_qt_runtime_smoke_desktop_result_report",
    "summarize_qt_runtime_smoke_desktop_result_report",
]
