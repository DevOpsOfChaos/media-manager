from __future__ import annotations

from media_manager.core.gui_review_workbench_view_models import (
    build_review_workbench_lane_filter,
    build_review_workbench_lanes,
    build_review_workbench_selection_options,
    build_ui_review_workbench_view_model,
    filter_review_workbench_lanes,
)


def _lanes():
    return build_review_workbench_lanes(
        duplicate_review={
            "run_count": 1,
            "review_candidate_count": 2,
            "latest_run": {"path": "runs/duplicates/latest.json"},
        },
        similar_images={"run_count": 0, "review_candidate_count": 0},
        people_review_summary={"group_count": 0, "face_count": 0},
        decision_summary={"error_count": 1, "review_candidate_count": 0},
    )


def test_review_workbench_filter_keeps_attention_lanes_without_running_commands() -> None:
    lanes = _lanes()

    filter_model = build_review_workbench_lane_filter(lanes, status="needs-review")
    filtered = filter_review_workbench_lanes(lanes, status="needs-review")

    assert filter_model["status"] == "needs_review"
    assert filter_model["executes_commands"] is False
    assert filter_model["attention_lane_ids"] == ["duplicates", "decision-summary"]
    assert [lane["lane_id"] for lane in filtered] == ["duplicates", "decision-summary"]


def test_review_workbench_filter_searches_titles_descriptions_and_routes() -> None:
    lanes = _lanes()

    filtered = filter_review_workbench_lanes(lanes, query="people")

    assert [lane["lane_id"] for lane in filtered] == ["people-review"]


def test_review_workbench_exposes_selection_options_for_future_qt_controls() -> None:
    lanes = _lanes()

    options = build_review_workbench_selection_options(lanes)

    assert [option["id"] for option in options] == [
        "duplicates",
        "similar-images",
        "people-review",
        "decision-summary",
    ]
    assert options[0]["has_attention"] is True
    assert options[0]["executes_immediately"] is False
    assert options[1]["status"] == "empty"


def test_review_workbench_view_model_carries_filtered_lanes_without_changing_primary_selection() -> None:
    model = build_ui_review_workbench_view_model(
        duplicate_review={"run_count": 1, "review_candidate_count": 2},
        similar_images={"run_count": 0, "review_candidate_count": 0},
        people_review_summary={"group_count": 1, "face_count": 2},
        decision_summary={"error_count": 0, "review_candidate_count": 0},
        selected_lane_id="people-review",
        lane_status_filter="needs_review",
    )

    assert model["selected_lane_id"] == "people-review"
    assert model["lane_filter"]["status"] == "needs_review"
    assert [lane["lane_id"] for lane in model["filtered_lanes"]] == ["duplicates", "people-review"]
    assert model["summary"]["filtered_lane_count"] == 2
    assert model["summary"]["selection_option_count"] == 4
    assert model["capabilities"]["executes_commands"] is False
