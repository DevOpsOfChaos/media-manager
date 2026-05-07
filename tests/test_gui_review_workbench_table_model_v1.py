from __future__ import annotations

from media_manager.core.gui_review_workbench_table_model import (
    build_review_workbench_table_columns,
    build_review_workbench_table_model,
    build_review_workbench_table_row,
    paginate_review_workbench_lanes,
)
from media_manager.core.gui_review_workbench_view_models import build_review_workbench_lanes, sort_review_workbench_lanes


def _lanes():
    lanes = build_review_workbench_lanes(
        duplicate_review={"run_count": 1, "review_candidate_count": 2, "latest_run": {"path": "runs/dup.json"}},
        similar_images={"run_count": 3, "review_candidate_count": 0},
        people_review_summary={"group_count": 1, "face_count": 4},
        decision_summary={"error_count": 1, "review_candidate_count": 0},
    )
    return sort_review_workbench_lanes(lanes, mode="attention_first")


def test_review_workbench_table_columns_are_stable_for_qt_headers() -> None:
    columns = build_review_workbench_table_columns()

    assert [column["id"] for column in columns] == [
        "title",
        "status",
        "attention_count",
        "item_count",
        "latest_run_path",
        "page_id",
    ]
    assert columns[0]["role"] == "primary_text"


def test_review_workbench_table_row_marks_selection_without_execution() -> None:
    row = build_review_workbench_table_row(_lanes()[0], selected_lane_id="duplicates")

    assert row["id"] == "duplicates"
    assert row["selected"] is True
    assert row["has_attention"] is True
    assert row["latest_run_path"] == "runs/dup.json"
    assert row["executes_immediately"] is False


def test_review_workbench_table_paginates_sorted_filtered_lanes() -> None:
    lanes = _lanes()

    pagination = paginate_review_workbench_lanes(lanes, page=2, page_size=2)
    table = build_review_workbench_table_model(lanes, selected_lane_id="people-review", page=2, page_size=2)

    assert pagination["visible_lane_ids"] == ["people-review", "people-setup"]
    assert table["pagination"]["page"] == 2
    assert [row["lane_id"] for row in table["rows"]] == ["people-review", "people-setup"]
    assert table["summary"]["selected_row_count"] == 1
    assert table["capabilities"]["executes_commands"] is False
