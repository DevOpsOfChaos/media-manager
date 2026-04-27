from __future__ import annotations


def passing_results() -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_result_collector",
        "results": [
            {"check_id": "read-command", "label": "Read command", "required": True, "passed": True},
            {"check_id": "confirm-local-only", "label": "Confirm local-only", "required": True, "passed": True},
            {"check_id": "confirm-window-title", "label": "Confirm window title", "required": True, "passed": True, "evidence_path": "local/screens/window.png"},
            {"check_id": "confirm-active-page", "label": "Confirm active page", "required": True, "passed": True},
            {"check_id": "confirm-no-auto-apply", "label": "Confirm no auto apply", "required": True, "passed": True},
        ],
    }


def failing_results() -> dict[str, object]:
    payload = passing_results()
    payload["results"][4]["passed"] = False
    payload["results"][4]["note"] = "Apply button started unexpectedly"
    return payload


def missing_results() -> dict[str, object]:
    payload = passing_results()
    payload["results"][2]["passed"] = None
    return payload

from media_manager.core.gui_qt_runtime_smoke_desktop_result_audit import audit_qt_runtime_smoke_desktop_results
from media_manager.core.gui_qt_runtime_smoke_desktop_result_decision import build_qt_runtime_smoke_desktop_result_decision
from media_manager.core.gui_qt_runtime_smoke_desktop_result_report import build_qt_runtime_smoke_desktop_result_report, summarize_qt_runtime_smoke_desktop_result_report
from media_manager.core.gui_qt_runtime_smoke_desktop_result_summary import summarize_qt_runtime_smoke_desktop_results
from media_manager.core.gui_qt_runtime_smoke_desktop_result_validator import validate_qt_runtime_smoke_desktop_results


def test_result_decision_and_report_accept_passing_results() -> None:
    validation = validate_qt_runtime_smoke_desktop_results(passing_results())
    summary = summarize_qt_runtime_smoke_desktop_results(validation)
    audit = audit_qt_runtime_smoke_desktop_results(validation)
    decision = build_qt_runtime_smoke_desktop_result_decision(summary, audit)
    report = build_qt_runtime_smoke_desktop_result_report(validation, summary, audit, decision)

    assert decision["decision"] == "accepted"
    assert report["accepted"] is True
    assert "Accepted: True" in summarize_qt_runtime_smoke_desktop_result_report(report)


def test_result_decision_needs_results_for_missing_required() -> None:
    validation = validate_qt_runtime_smoke_desktop_results(missing_results())
    summary = summarize_qt_runtime_smoke_desktop_results(validation)
    audit = audit_qt_runtime_smoke_desktop_results(validation)
    decision = build_qt_runtime_smoke_desktop_result_decision(summary, audit)

    assert decision["decision"] == "blocked"
    assert decision["executes_immediately"] is False
