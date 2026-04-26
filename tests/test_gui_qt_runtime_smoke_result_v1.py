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

from media_manager.core.gui_qt_runtime_smoke_result import (
    build_qt_runtime_smoke_result,
    build_qt_runtime_smoke_result_from_check,
    normalize_qt_runtime_smoke_results,
    summarize_qt_runtime_smoke_results,
)


def test_smoke_result_is_local_headless_data() -> None:
    result = build_qt_runtime_smoke_result(
        "local-only",
        passed=True,
        category="privacy",
        reviewer="manual",
        recorded_at_utc="2026-04-26T20:00:00Z",
    )

    assert result["check_id"] == "local-only"
    assert result["passed"] is True
    assert result["category"] == "privacy"
    assert result["capabilities"]["local_only"] is True
    assert result["capabilities"]["opens_window"] is False


def test_smoke_result_normalization_and_summary() -> None:
    check = {"id": "face-assets-not-uploaded", "category": "privacy", "required": True}
    result = build_qt_runtime_smoke_result_from_check(check, passed=False, note="manual fail")
    normalized = normalize_qt_runtime_smoke_results([result, {"check_id": "launch-window", "passed": True}])
    summary = summarize_qt_runtime_smoke_results(normalized)

    assert normalized[0]["note"] == "manual fail"
    assert summary["result_count"] == 2
    assert summary["failed_required_count"] == 1
    assert summary["privacy_result_count"] == 1
