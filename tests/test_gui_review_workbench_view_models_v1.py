from __future__ import annotations

import sys

from media_manager.core.gui_review_workbench_view_models import (
    build_review_workbench_lanes,
    build_ui_review_workbench_view_model,
)


def _duplicate_model() -> dict[str, object]:
    return {
        "kind": "ui_duplicate_review_view_model",
        "run_count": 1,
        "review_candidate_count": 3,
        "latest_run": {"path": "C:/runs/duplicates", "command": "duplicates"},
        "apply_enabled": False,
    }


def _similar_model() -> dict[str, object]:
    return {
        "kind": "ui_similar_images_view_model",
        "run_count": 1,
        "review_candidate_count": 2,
        "latest_run": {"path": "C:/runs/similar", "command": "similar-images"},
        "apply_enabled": False,
    }


def _decision_model() -> dict[str, object]:
    return {
        "kind": "ui_decision_summary_view_model",
        "status": "blocked",
        "review_candidate_count": 5,
        "error_count": 1,
        "apply_enabled": False,
    }


def test_review_workbench_builds_lanes_without_qt_import() -> None:
    sys.modules.pop("PySide6", None)
    workbench = build_ui_review_workbench_view_model(
        duplicate_review=_duplicate_model(),
        similar_images=_similar_model(),
        decision_summary=_decision_model(),
        people_review_summary={"group_count": 4, "face_count": 12},
    )
    assert workbench["kind"] == "ui_review_workbench_view_model"
    assert workbench["summary"]["lane_count"] == 7
    assert workbench["summary"]["attention_count"] == 17
    assert workbench["active_lane_id"] == "duplicates"
    assert workbench["capabilities"]["executes_commands"] is False
    assert workbench["capabilities"]["apply_enabled"] is False
    assert "PySide6" not in sys.modules


def test_review_workbench_lanes_are_safe_navigation_contracts() -> None:
    lanes = build_review_workbench_lanes(
        duplicate_review=_duplicate_model(),
        similar_images=_similar_model(),
        decision_summary=_decision_model(),
        people_review_summary={"group_count": 0, "face_count": 0},
    )
    assert [lane["lane_id"] for lane in lanes] == ["duplicates", "similar-images", "similar-review", "people-setup", "people-review", "decision-summary", "trip-manager"]
    assert all(lane["primary_action"]["executes_immediately"] is False for lane in lanes)
    assert all(lane["executes_commands"] is False for lane in lanes)
    assert lanes[4]["status"] == "empty"
