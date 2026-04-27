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
from media_manager.core.gui_qt_runtime_smoke_desktop_result_summary import summarize_qt_runtime_smoke_desktop_results
from media_manager.core.gui_qt_runtime_smoke_desktop_result_validator import validate_qt_runtime_smoke_desktop_results


def test_result_summary_and_audit_accept_clean_results() -> None:
    validation = validate_qt_runtime_smoke_desktop_results(passing_results())
    summary = summarize_qt_runtime_smoke_desktop_results(validation)
    audit = audit_qt_runtime_smoke_desktop_results(validation)

    assert summary["passed"] is True
    assert summary["complete"] is True
    assert summary["evidence_count"] == 1
    assert audit["valid"] is True
    assert audit["problem_count"] == 0


def test_result_audit_blocks_sensitive_media() -> None:
    payload = passing_results()
    payload["results"][0]["contains_sensitive_media"] = True
    validation = validate_qt_runtime_smoke_desktop_results(payload)
    audit = audit_qt_runtime_smoke_desktop_results(validation)

    assert audit["valid"] is False
    assert audit["problem_count"] >= 1
