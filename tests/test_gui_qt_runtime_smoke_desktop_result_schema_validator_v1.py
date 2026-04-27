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

from media_manager.core.gui_qt_runtime_smoke_desktop_result_schema import build_qt_runtime_smoke_desktop_result_schema, normalize_qt_runtime_smoke_desktop_result
from media_manager.core.gui_qt_runtime_smoke_desktop_result_validator import validate_qt_runtime_smoke_desktop_results


def test_result_schema_and_validator_accept_passing_results() -> None:
    schema = build_qt_runtime_smoke_desktop_result_schema()
    validation = validate_qt_runtime_smoke_desktop_results(passing_results())

    assert schema["summary"]["field_count"] == 8
    assert validation["valid"] is True
    assert validation["summary"]["result_count"] == 5
    assert validation["summary"]["passed_required_count"] == 5
    assert validation["summary"]["sensitive_media_count"] == 0


def test_result_validator_flags_failed_and_missing_required_results() -> None:
    failed = validate_qt_runtime_smoke_desktop_results(failing_results())
    missing = validate_qt_runtime_smoke_desktop_results(missing_results())

    assert failed["valid"] is False
    assert failed["summary"]["failed_required_count"] == 1
    assert missing["valid"] is False
    assert missing["summary"]["missing_required_count"] == 1


def test_normalize_result_redacts_evidence_presence() -> None:
    result = normalize_qt_runtime_smoke_desktop_result({"check_id": "x", "passed": True, "evidence_path": "local/file.png"})

    assert result["has_evidence_path"] is True
    assert result["local_only"] is True
