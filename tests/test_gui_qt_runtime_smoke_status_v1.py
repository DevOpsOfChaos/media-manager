from __future__ import annotations


def sample_smoke_report(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_report", "active_page_id": "people-review", "ready_for_release_gate": ready, "summary": {"check_count": 4, "result_count": 4, "problem_count": problems, "privacy_check_count": 2, "ready_for_release_gate": ready}}


def sample_history() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_history", "entries": [{"recorded_at_utc": "2026-04-26T20:00:00Z", "active_page_id": "dashboard", "ready_for_release_gate": False, "problem_count": 1, "privacy_check_count": 0, "commit_sha": "a"}, {"recorded_at_utc": "2026-04-26T21:00:00Z", "active_page_id": "people-review", "ready_for_release_gate": True, "problem_count": 0, "privacy_check_count": 2, "commit_sha": "b"}]}


def sample_artifact_manifest() -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_artifact_manifest", "summary": {"artifact_count": 2, "metadata_only_count": 2, "sensitive_media_count": 0, "all_local_only": True}}

from media_manager.core.gui_qt_runtime_smoke_status import build_qt_runtime_smoke_status_badge, build_qt_runtime_smoke_status_strip


def test_status_badge_marks_ready_and_blocked_states() -> None:
    ready = build_qt_runtime_smoke_status_badge(sample_smoke_report())
    blocked = build_qt_runtime_smoke_status_badge(sample_smoke_report(ready=False, problems=2))
    assert ready["state"] == "ready"
    assert ready["severity"] == "success"
    assert blocked["state"] == "blocked"
    assert blocked["severity"] == "error"


def test_status_strip_summarizes_multiple_badges() -> None:
    strip = build_qt_runtime_smoke_status_strip([sample_smoke_report(), sample_smoke_report(ready=False, problems=1), {"summary": {"missing_required_count": 1}}])
    assert strip["summary"]["badge_count"] == 3
    assert strip["summary"]["ready_count"] == 1
    assert strip["summary"]["blocked_count"] == 1
    assert strip["summary"]["incomplete_count"] == 1
