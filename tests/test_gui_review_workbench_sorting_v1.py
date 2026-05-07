from __future__ import annotations

from media_manager.core.gui_review_workbench_view_models import (
    build_review_workbench_lane_sort,
    build_review_workbench_lanes,
    build_ui_review_workbench_view_model,
    sort_review_workbench_lanes,
)


def _lanes():
    return build_review_workbench_lanes(
        duplicate_review={"run_count": 1, "review_candidate_count": 2},
        similar_images={"run_count": 4, "review_candidate_count": 0},
        people_review_summary={"group_count": 1, "face_count": 3},
        decision_summary={"error_count": 1, "review_candidate_count": 0},
    )


def test_review_workbench_lane_sort_normalizes_modes_without_commands() -> None:
    sort_model = build_review_workbench_lane_sort(mode="attention-first")
    fallback = build_review_workbench_lane_sort(mode="unknown")

    assert sort_model["mode"] == "attention_first"
    assert sort_model["executes_commands"] is False
    assert fallback["mode"] == "attention_first"
    assert "title" in sort_model["available_modes"]


def test_review_workbench_sorts_attention_lanes_before_passive_lanes() -> None:
    sorted_lanes = sort_review_workbench_lanes(_lanes(), mode="attention_first")

    assert [lane["lane_id"] for lane in sorted_lanes] == [
        "duplicates",
        "decision-summary",
        "people-review",
        "people-setup",
        "similar-images",
        "similar-review",
        "trip-manager",
    ]


def test_review_workbench_sorts_by_item_count_without_mutating_source_order() -> None:
    lanes = _lanes()
    sorted_lanes = sort_review_workbench_lanes(lanes, mode="item_count")

    assert [lane["lane_id"] for lane in lanes] == [
        "duplicates",
        "similar-images",
        "similar-review",
        "people-setup",
        "people-review",
        "decision-summary",
        "trip-manager",
    ]
    assert [lane["lane_id"] for lane in sorted_lanes] == [
        "similar-images",
        "similar-review",
        "people-review",
        "duplicates",
        "decision-summary",
        "people-setup",
        "trip-manager",
    ]


def test_review_workbench_view_model_exposes_sorted_filtered_lanes_for_qt_lists() -> None:
    model = build_ui_review_workbench_view_model(
        duplicate_review={"run_count": 1, "review_candidate_count": 2},
        similar_images={"run_count": 4, "review_candidate_count": 0},
        people_review_summary={"group_count": 1, "face_count": 3},
        decision_summary={"error_count": 1, "review_candidate_count": 0},
        lane_status_filter="needs_review",
        lane_sort_mode="lane-id",
    )

    assert model["lane_sort"]["mode"] == "lane_id"
    assert [lane["lane_id"] for lane in model["filtered_lanes"]] == [
        "duplicates",
        "people-review",
        "decision-summary",
    ]
    assert [lane["lane_id"] for lane in model["sorted_filtered_lanes"]] == [
        "decision-summary",
        "duplicates",
        "people-review",
    ]
    assert model["summary"]["sorted_filtered_lane_count"] == 3
    assert model["summary"]["lane_sort_mode"] == "lane_id"
    assert model["capabilities"]["executes_commands"] is False
