from __future__ import annotations

from media_manager.core.gui_review_workbench_controller import (
    build_review_workbench_update_intent,
    build_review_workbench_view_state,
    reduce_review_workbench_state,
)


def _view_state(**overrides):
    payload = {
        "duplicate_review": {"run_count": 1, "review_candidate_count": 2},
        "similar_images": {"run_count": 4, "review_candidate_count": 0},
        "people_review_summary": {"group_count": 1, "face_count": 3},
        "decision_summary": {"error_count": 1, "review_candidate_count": 0},
    }
    payload.update(overrides)
    return build_review_workbench_view_state(**payload)


def test_review_workbench_controller_combines_view_model_and_table_model() -> None:
    state = _view_state(lane_status_filter="needs_review", lane_sort_mode="lane-id", page=1, page_size=2)

    assert state["kind"] == "ui_review_workbench_controller_state"
    assert state["view_model"]["summary"]["filtered_lane_count"] == 3
    assert state["table_model"]["summary"]["row_count"] == 2
    assert state["state"]["lane_sort_mode"] == "lane_id"
    assert state["capabilities"]["requires_pyside6"] is False
    assert state["capabilities"]["executes_commands"] is False


def test_review_workbench_reducer_updates_filter_sort_page_without_commands() -> None:
    state = _view_state()["state"]

    filtered = reduce_review_workbench_state(
        state,
        build_review_workbench_update_intent("set-filter", status="needs-review"),
    )
    sorted_state = reduce_review_workbench_state(
        filtered["state"],
        build_review_workbench_update_intent("set-sort", sort_mode="lane-id"),
    )
    paged = reduce_review_workbench_state(
        sorted_state["state"],
        build_review_workbench_update_intent("set-page", page=2),
    )

    assert filtered["state"]["lane_status_filter"] == "needs-review"
    assert filtered["state"]["page"] == 1
    assert sorted_state["state"]["lane_sort_mode"] == "lane-id"
    assert paged["state"]["page"] == 2
    assert paged["executes_commands"] is False


def test_review_workbench_reducer_can_reset_view_state() -> None:
    state = {
        "selected_lane_id": "people-review",
        "lane_status_filter": "needs_review",
        "lane_query": "people",
        "lane_sort_mode": "lane_id",
        "page": 4,
        "page_size": 12,
    }

    reset = reduce_review_workbench_state(state, build_review_workbench_update_intent("reset-view"))

    assert reset["state"] == {
        "selected_lane_id": None,
        "lane_status_filter": "all",
        "lane_query": "",
        "lane_sort_mode": "attention_first",
        "page": 1,
        "page_size": 12,
    }
    assert reset["changed"] is True
