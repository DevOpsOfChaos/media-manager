from __future__ import annotations

from media_manager.core.gui_review_workbench_view_models import (
    build_review_workbench_lane_detail,
    build_ui_review_workbench_view_model,
)


def test_review_workbench_lane_detail_explains_attention_without_commands() -> None:
    model = build_ui_review_workbench_view_model(
        duplicate_review={"run_count": 1, "review_candidate_count": 2, "latest_run": {"path": "runs/dup.json"}},
        similar_images={"run_count": 0, "review_candidate_count": 0},
        people_review_summary={"group_count": 0, "face_count": 0},
        decision_summary={"error_count": 0, "review_candidate_count": 0},
        selected_lane_id="duplicates",
    )

    detail = model["selected_lane_detail"]

    assert detail["kind"] == "ui_review_workbench_lane_detail"
    assert detail["lane_id"] == "duplicates"
    assert detail["has_attention"] is True
    assert detail["has_latest_run"] is True
    assert "needs review" in detail["headline"]
    assert detail["executes_commands"] is False
    assert detail["requires_pyside6"] is False


def test_review_workbench_lane_detail_handles_empty_selection() -> None:
    detail = build_review_workbench_lane_detail(None)

    assert detail["lane_id"] is None
    assert detail["status"] == "empty"
    assert detail["primary_action"] is None
    assert detail["recommended_next_step"] == "Select a review lane before navigating."
    assert detail["executes_commands"] is False
