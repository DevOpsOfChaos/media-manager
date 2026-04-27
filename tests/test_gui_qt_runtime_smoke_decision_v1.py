from __future__ import annotations


def sample_smoke_report(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_report", "active_page_id": "people-review", "ready_for_release_gate": ready, "summary": {"check_count": 4, "result_count": 4, "problem_count": problems, "privacy_check_count": 2, "ready_for_release_gate": ready}}


def sample_history() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_history", "entries": [{"recorded_at_utc": "2026-04-26T20:00:00Z", "active_page_id": "dashboard", "ready_for_release_gate": False, "problem_count": 1, "privacy_check_count": 0, "commit_sha": "a"}, {"recorded_at_utc": "2026-04-26T21:00:00Z", "active_page_id": "people-review", "ready_for_release_gate": True, "problem_count": 0, "privacy_check_count": 2, "commit_sha": "b"}]}


def sample_artifact_manifest() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_artifact_manifest", "summary": {"artifact_count": 2, "metadata_only_count": 2, "sensitive_media_count": 0, "all_local_only": True}}

from media_manager.core.gui_qt_runtime_smoke_dashboard import build_qt_runtime_smoke_dashboard
from media_manager.core.gui_qt_runtime_smoke_decision import build_qt_runtime_smoke_decision, summarize_qt_runtime_smoke_decision


def test_smoke_decision_recommends_manual_smoke_when_ready() -> None:
    dashboard = build_qt_runtime_smoke_dashboard(current_report=sample_smoke_report(), history=sample_history(), artifact_manifest=sample_artifact_manifest())
    decision = build_qt_runtime_smoke_decision(dashboard)
    assert decision["decision"] == "ready_for_manual_qt_smoke"
    assert decision["severity"] == "success"
    assert decision["requires_user_confirmation"] is True
    assert decision["executes_immediately"] is False
    assert decision["opens_window"] is False
    assert "Executes immediately: False" in summarize_qt_runtime_smoke_decision(decision)


def test_smoke_decision_blocks_failed_runtime_smoke() -> None:
    dashboard = build_qt_runtime_smoke_dashboard(current_report=sample_smoke_report(ready=False, problems=1), history=sample_history(), artifact_manifest=sample_artifact_manifest())
    decision = build_qt_runtime_smoke_decision(dashboard)
    assert decision["decision"] == "blocked"
    assert decision["severity"] == "error"
