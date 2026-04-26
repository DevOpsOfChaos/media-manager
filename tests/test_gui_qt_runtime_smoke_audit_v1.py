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

from media_manager.core.gui_qt_runtime_smoke_audit import audit_qt_runtime_smoke_session
from media_manager.core.gui_qt_runtime_smoke_session import build_qt_runtime_smoke_session


def test_smoke_audit_accepts_complete_privacy_safe_session() -> None:
    session = build_qt_runtime_smoke_session(sample_smoke_plan(), passing_results())
    audit = audit_qt_runtime_smoke_session(session)

    assert audit["valid"] is True
    assert audit["problem_count"] == 0
    assert audit["summary"]["privacy_check_count"] == 2
    assert audit["summary"]["passed_privacy_check_count"] == 2


def test_smoke_audit_rejects_failed_privacy_check() -> None:
    results = passing_results()
    results["face-assets-not-uploaded"] = False
    session = build_qt_runtime_smoke_session(sample_smoke_plan(), results)
    audit = audit_qt_runtime_smoke_session(session)

    assert audit["valid"] is False
    codes = {problem["code"] for problem in audit["problems"]}
    assert "failed_required_smoke_check" in codes
    assert "privacy_smoke_failed" in codes
