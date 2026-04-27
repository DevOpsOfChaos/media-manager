from __future__ import annotations


def sample_smoke_report(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_report", "active_page_id": "people-review", "ready_for_release_gate": ready, "summary": {"check_count": 4, "result_count": 4, "problem_count": problems, "privacy_check_count": 2, "ready_for_release_gate": ready}}


def sample_history() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_history", "entries": [{"recorded_at_utc": "2026-04-26T20:00:00Z", "active_page_id": "dashboard", "ready_for_release_gate": False, "problem_count": 1, "privacy_check_count": 0, "commit_sha": "a"}, {"recorded_at_utc": "2026-04-26T21:00:00Z", "active_page_id": "people-review", "ready_for_release_gate": True, "problem_count": 0, "privacy_check_count": 2, "commit_sha": "b"}]}


def sample_artifact_manifest() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_artifact_manifest", "summary": {"artifact_count": 2, "metadata_only_count": 2, "sensitive_media_count": 0, "all_local_only": True}}

from media_manager.core.gui_qt_runtime_smoke_trend import build_qt_runtime_smoke_trend


def test_smoke_trend_detects_improvement() -> None:
    trend = build_qt_runtime_smoke_trend(sample_history())
    assert trend["summary"]["entry_count"] == 2
    assert trend["summary"]["ready_count"] == 1
    assert trend["summary"]["direction"] == "improved"
    assert trend["summary"]["latest_active_page_id"] == "people-review"
    assert trend["summary"]["latest_problem_count"] == 0


def test_smoke_trend_handles_empty_history() -> None:
    trend = build_qt_runtime_smoke_trend([])
    assert trend["summary"]["entry_count"] == 0
    assert trend["summary"]["direction"] == "empty"
