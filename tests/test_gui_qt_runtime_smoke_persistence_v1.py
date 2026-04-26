from __future__ import annotations


def sample_smoke_report() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "kind": "qt_runtime_smoke_report",
        "active_page_id": "people-review",
        "reviewer": "Manuel",
        "handoff_ready": True,
        "launch_ready": True,
        "ready_for_release_gate": True,
        "session": {
            "kind": "qt_runtime_smoke_session",
            "active_page_id": "people-review",
            "complete": True,
            "summary": {
                "check_count": 4,
                "result_count": 4,
                "missing_required_count": 0,
                "failed_required_count": 0,
                "privacy_check_count": 2,
            },
            "missing_required_checks": [],
            "failed_required_checks": [],
            "results": [
                {
                    "kind": "qt_runtime_smoke_result",
                    "check_id": "launch-window",
                    "passed": True,
                    "required": True,
                    "category": "startup",
                    "note": "ok",
                    "evidence_path": "C:/Users/mries/Pictures/screenshot.png",
                },
                {
                    "kind": "qt_runtime_smoke_result",
                    "check_id": "local-only",
                    "passed": True,
                    "required": True,
                    "category": "privacy",
                    "note": "no upload",
                    "evidence_path": None,
                },
            ],
        },
        "audit": {
            "kind": "qt_runtime_smoke_audit",
            "valid": True,
            "problem_count": 0,
            "problems": [],
            "summary": {"privacy_check_count": 2, "passed_privacy_check_count": 2},
        },
        "summary": {
            "check_count": 4,
            "result_count": 4,
            "missing_required_count": 0,
            "failed_required_count": 0,
            "privacy_check_count": 2,
            "problem_count": 0,
            "ready_for_release_gate": True,
        },
    }

import json

import pytest

from media_manager.core.gui_qt_runtime_smoke_persistence import (
    load_qt_runtime_smoke_report,
    read_json_object,
    save_qt_runtime_smoke_report,
    smoke_report_file_summary,
)


def test_smoke_report_persistence_round_trips_json_object(tmp_path) -> None:
    path = tmp_path / "runtime-smoke-report.json"
    write = save_qt_runtime_smoke_report(path, sample_smoke_report())

    loaded = load_qt_runtime_smoke_report(path)
    summary = smoke_report_file_summary(path)

    assert write["bytes_written"] > 0
    assert loaded["active_page_id"] == "people-review"
    assert loaded["ready_for_release_gate"] is True
    assert summary["problem_count"] == 0
    assert summary["local_only"] is True


def test_read_json_object_rejects_arrays(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    with pytest.raises(ValueError):
        read_json_object(path)
