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

from media_manager.core.gui_qt_runtime_smoke_session import build_qt_runtime_smoke_session


def test_smoke_session_merges_plan_with_results() -> None:
    session = build_qt_runtime_smoke_session(sample_smoke_plan(), passing_results(), reviewer="Manuel")

    assert session["complete"] is True
    assert session["reviewer"] == "Manuel"
    assert session["summary"]["check_count"] == 4
    assert session["summary"]["missing_required_count"] == 0
    assert session["summary"]["failed_required_count"] == 0
    assert session["summary"]["privacy_check_count"] == 2


def test_smoke_session_tracks_missing_required_checks() -> None:
    results = {"launch-window": True, "navigation-visible": True}
    session = build_qt_runtime_smoke_session(sample_smoke_plan(), results)

    assert session["complete"] is False
    assert session["missing_required_checks"] == ["local-only", "face-assets-not-uploaded"]
    assert session["summary"]["missing_required_count"] == 2
