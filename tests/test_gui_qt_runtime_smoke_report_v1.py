from __future__ import annotations


def sample_smoke_plan() -> dict[str, object]:
    return {
        "kind": "qt_runtime_manual_smoke_plan",
        "language": "en",
        "active_page_id": "people-review",
        "checks": [
            {"id": "launch-window", "label": "Window opens", "required": True, "category": "startup"},
            {"id": "navigation-visible", "label": "Navigation visible", "required": True, "category": "shell"},
            {"id": "local-only", "label": "Local only", "required": True, "category": "privacy"},
            {"id": "face-assets-not-uploaded", "label": "No upload", "required": True, "category": "privacy"},
        ],
        "summary": {"check_count": 4, "required_check_count": 4, "privacy_check_count": 2},
    }


def sample_handoff_manifest() -> dict[str, object]:
    return {
        "kind": "qt_runtime_handoff_manifest",
        "active_page_id": "people-review",
        "ready_for_manual_smoke": True,
        "privacy": {"local_only": True, "contains_sensitive_people_data": True},
    }


def sample_launch_contract() -> dict[str, object]:
    return {
        "kind": "qt_runtime_launch_contract",
        "active_page_id": "people-review",
        "ready_for_launch_attempt": True,
        "execution_policy": {"mode": "manual_only", "executes_immediately": False},
    }


def passing_results() -> dict[str, bool]:
    return {
        "launch-window": True,
        "navigation-visible": True,
        "local-only": True,
        "face-assets-not-uploaded": True,
    }

from media_manager.core.gui_qt_runtime_smoke_report import (
    build_qt_runtime_smoke_report,
    summarize_qt_runtime_smoke_report,
)


def test_smoke_report_ready_when_handoff_launch_and_smoke_pass() -> None:
    report = build_qt_runtime_smoke_report(
        sample_handoff_manifest(),
        sample_launch_contract(),
        sample_smoke_plan(),
        passing_results(),
        reviewer="Manuel",
    )

    assert report["ready_for_release_gate"] is True
    assert report["handoff_ready"] is True
    assert report["launch_ready"] is True
    assert report["summary"]["problem_count"] == 0
    assert "Ready for release gate: True" in summarize_qt_runtime_smoke_report(report)


def test_smoke_report_not_ready_when_launch_contract_not_ready() -> None:
    launch = sample_launch_contract()
    launch["ready_for_launch_attempt"] = False
    report = build_qt_runtime_smoke_report(
        sample_handoff_manifest(),
        launch,
        sample_smoke_plan(),
        passing_results(),
    )

    assert report["ready_for_release_gate"] is False
    assert report["launch_ready"] is False
