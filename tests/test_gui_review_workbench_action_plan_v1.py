from __future__ import annotations

from media_manager.core.gui_review_workbench_action_plan import (
    build_review_workbench_action_plan,
    find_review_workbench_action,
)
from media_manager.core.gui_review_workbench_view_models import build_ui_review_workbench_view_model


def test_review_workbench_action_plan_keeps_apply_disabled_and_navigation_safe() -> None:
    view_model = build_ui_review_workbench_view_model(
        duplicate_review={"run_count": 1, "review_candidate_count": 2},
        similar_images={"run_count": 0, "review_candidate_count": 0},
        people_review_summary={"group_count": 0, "face_count": 0},
        decision_summary={"error_count": 0, "review_candidate_count": 0},
        selected_lane_id="duplicates",
        lane_status_filter="needs_review",
    )

    plan = build_review_workbench_action_plan(view_model)
    open_action = find_review_workbench_action(plan, "open-selected-lane")
    apply_action = find_review_workbench_action(plan, "apply-reviewed-decisions")
    reset_action = find_review_workbench_action(plan, "reset-review-filters")

    assert plan["kind"] == "ui_review_workbench_action_plan"
    assert open_action["enabled"] is True
    assert open_action["page_id"] == "run-history"
    assert reset_action["enabled"] is True
    assert apply_action["enabled"] is False
    assert apply_action["requires_explicit_user_confirmation"] is True
    assert plan["capabilities"]["executes_commands"] is False
    assert plan["capabilities"]["apply_enabled"] is False


def test_review_workbench_action_lookup_returns_none_for_unknown_actions() -> None:
    plan = build_review_workbench_action_plan({"selected_lane_id": None})

    assert find_review_workbench_action(plan, "missing") is None
    assert find_review_workbench_action(plan, "open-selected-lane")["enabled"] is False
