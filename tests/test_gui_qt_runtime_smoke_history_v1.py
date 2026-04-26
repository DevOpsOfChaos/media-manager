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

from media_manager.core.gui_qt_runtime_smoke_history import (
    append_qt_runtime_smoke_history_entry,
    build_qt_runtime_smoke_history_entry,
    summarize_qt_runtime_smoke_history,
)


def test_smoke_history_entry_and_append_summary() -> None:
    report = sample_smoke_report()
    entry = build_qt_runtime_smoke_history_entry(
        report,
        report_path="runs/runtime-smoke-report.json",
        commit_sha="abc123",
        recorded_at_utc="2026-04-26T20:00:00Z",
    )
    history = append_qt_runtime_smoke_history_entry([], report, report_path="runs/runtime-smoke-report.json")
    summary = summarize_qt_runtime_smoke_history(history)

    assert entry["active_page_id"] == "people-review"
    assert entry["ready_for_release_gate"] is True
    assert entry["privacy_check_count"] == 2
    assert history["summary"]["entry_count"] == 1
    assert summary["ready_count"] == 1
    assert summary["latest_active_page_id"] == "people-review"


def test_smoke_history_tracks_not_ready_entries() -> None:
    report = sample_smoke_report()
    report["ready_for_release_gate"] = False
    report["summary"]["problem_count"] = 2
    history = append_qt_runtime_smoke_history_entry([], report)
    summary = summarize_qt_runtime_smoke_history(history)

    assert summary["not_ready_count"] == 1
    assert summary["problem_count_total"] == 2
