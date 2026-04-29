from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_runtime_smoke_audit import audit_qt_runtime_smoke_session
from .gui_qt_runtime_smoke_session import build_qt_runtime_smoke_session

QT_RUNTIME_SMOKE_REPORT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: object, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def build_qt_runtime_smoke_report(
    handoff_manifest: Mapping[str, Any],
    launch_contract: Mapping[str, Any],
    smoke_plan: Mapping[str, Any],
    results: Mapping[str, bool] | list[Mapping[str, Any]],
    *,
    reviewer: str = "",
) -> dict[str, object]:
    """Build the final manual-smoke report for the current Qt runtime handoff.

    Manual launch readiness is separate from manual evidence completeness:
    a Qt page can be ready to start manual smoke before recorded evidence exists.
    """

    session = build_qt_runtime_smoke_session(smoke_plan, results, reviewer=reviewer)
    audit = audit_qt_runtime_smoke_session(session)
    handoff_ready = bool(handoff_manifest.get("ready_for_manual_smoke"))
    launch_ready = bool(launch_contract.get("ready_for_launch_attempt"))
    ready_for_manual_smoke = handoff_ready and launch_ready
    evidence_complete = bool(audit.get("valid"))
    ready_for_release_gate = ready_for_manual_smoke and evidence_complete

    session_summary = _mapping(session.get("summary"))
    audit_summary = _mapping(audit.get("summary"))
    problem_count = _int(audit.get("problem_count"))
    incomplete_privacy_check_count = max(
        0,
        _int(audit_summary.get("privacy_check_count")) - _int(audit_summary.get("passed_privacy_check_count")),
    )

    return {
        "schema_version": QT_RUNTIME_SMOKE_REPORT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_report",
        "active_page_id": smoke_plan.get("active_page_id") or handoff_manifest.get("active_page_id") or launch_contract.get("active_page_id"),
        "reviewer": reviewer,
        "handoff_ready": handoff_ready,
        "launch_ready": launch_ready,
        "ready_for_manual_smoke": ready_for_manual_smoke,
        "ready_to_start_manual_smoke": ready_for_manual_smoke,
        "evidence_complete": evidence_complete,
        "ready_for_release_gate": ready_for_release_gate,
        "session": session,
        "audit": audit,
        "summary": {
            "check_count": session_summary.get("check_count", 0),
            "required_check_count": session_summary.get("required_check_count", 0),
            "result_count": session_summary.get("result_count", 0),
            "missing_required_count": _int(audit_summary.get("missing_required_count")),
            "failed_required_count": _int(audit_summary.get("failed_required_count")),
            "privacy_check_count": _int(audit_summary.get("privacy_check_count")),
            "passed_privacy_check_count": _int(audit_summary.get("passed_privacy_check_count")),
            "incomplete_privacy_check_count": incomplete_privacy_check_count,
            "problem_count": problem_count,
            "blocking_problem_count": 0 if ready_for_manual_smoke else problem_count,
            "manual_launch_problem_count": 0 if ready_for_manual_smoke else problem_count,
            "evidence_problem_count": problem_count,
            "ready_for_manual_smoke": ready_for_manual_smoke,
            "ready_to_start_manual_smoke": ready_for_manual_smoke,
            "evidence_complete": evidence_complete,
            "ready_for_release_gate": ready_for_release_gate,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }


def summarize_qt_runtime_smoke_report(report: Mapping[str, Any]) -> str:
    summary = _mapping(report.get("summary"))
    return "\n".join(
        [
            "Qt runtime smoke report",
            f"  Active page: {report.get('active_page_id')}",
            f"  Ready for manual smoke: {summary.get('ready_for_manual_smoke')}",
            f"  Evidence complete: {summary.get('evidence_complete')}",
            f"  Ready for release gate: {summary.get('ready_for_release_gate')}",
            f"  Checks: {summary.get('check_count', 0)}",
            f"  Results: {summary.get('result_count', 0)}",
            f"  Problems: {summary.get('problem_count', 0)}",
            f"  Privacy checks: {summary.get('privacy_check_count', 0)}",
        ]
    )


__all__ = ["QT_RUNTIME_SMOKE_REPORT_SCHEMA_VERSION", "build_qt_runtime_smoke_report", "summarize_qt_runtime_smoke_report"]
