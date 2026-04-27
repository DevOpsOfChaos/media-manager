from __future__ import annotations


def sample_smoke_report(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_report", "active_page_id": "people-review", "ready_for_release_gate": ready, "summary": {"check_count": 4, "result_count": 4, "problem_count": problems, "privacy_check_count": 2, "ready_for_release_gate": ready}}


def sample_history() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_history", "entries": [{"recorded_at_utc": "2026-04-26T20:00:00Z", "active_page_id": "dashboard", "ready_for_release_gate": False, "problem_count": 1, "privacy_check_count": 0, "commit_sha": "a"}, {"recorded_at_utc": "2026-04-26T21:00:00Z", "active_page_id": "people-review", "ready_for_release_gate": True, "problem_count": 0, "privacy_check_count": 2, "commit_sha": "b"}]}


def sample_artifact_manifest() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_artifact_manifest", "summary": {"artifact_count": 2, "metadata_only_count": 2, "sensitive_media_count": 0, "all_local_only": True}}

from media_manager.core.gui_qt_runtime_smoke_dashboard import build_qt_runtime_smoke_dashboard


def test_smoke_dashboard_combines_report_history_and_artifacts() -> None:
    dashboard = build_qt_runtime_smoke_dashboard(current_report=sample_smoke_report(), history=sample_history(), artifact_manifest=sample_artifact_manifest())
    assert dashboard["active_page_id"] == "people-review"
    assert dashboard["ready_for_runtime_review"] is True
    assert dashboard["summary"]["card_count"] == 3
    assert dashboard["summary"]["history_entry_count"] == 2
    assert dashboard["summary"]["artifact_count"] == 2
    assert dashboard["status_strip"]["summary"]["blocked_count"] == 0


def test_smoke_dashboard_not_ready_when_current_report_blocked() -> None:
    dashboard = build_qt_runtime_smoke_dashboard(current_report=sample_smoke_report(ready=False, problems=1), history=sample_history(), artifact_manifest=sample_artifact_manifest())
    assert dashboard["ready_for_runtime_review"] is False
    assert dashboard["summary"]["blocked_badge_count"] >= 1
