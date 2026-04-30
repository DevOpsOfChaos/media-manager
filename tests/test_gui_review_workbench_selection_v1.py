from __future__ import annotations

from media_manager.core.gui_review_workbench_view_models import build_ui_review_workbench_view_model


def _payload(**overrides):
    base = {
        "duplicate_review": {
            "run_count": 1,
            "review_candidate_count": 2,
            "latest_run": {"path": "runs/duplicates/latest.json"},
        },
        "similar_images": {
            "run_count": 1,
            "review_candidate_count": 0,
            "latest_run": {"path": "runs/similar/latest.json"},
        },
        "decision_summary": {"error_count": 0, "review_candidate_count": 0},
        "people_review_summary": {"group_count": 1, "face_count": 3},
    }
    base.update(overrides)
    return build_ui_review_workbench_view_model(**base)


def test_review_workbench_selects_requested_lane_without_executing_commands() -> None:
    model = _payload(selected_lane_id="similar-images")

    assert model["selected_lane_id"] == "similar-images"
    assert model["active_lane_id"] == "similar-images"
    assert model["selected_lane"]["lane_id"] == "similar-images"
    assert model["navigation_target_page_id"] == "run-history"
    assert model["latest_run_path"] == "runs/similar/latest.json"
    assert model["primary_action"]["executes_immediately"] is False
    assert model["toolbar"]["executes_commands"] is False
    assert all(action["executes_immediately"] is False for action in model["toolbar"]["actions"])
    assert model["toolbar"]["actions"][2]["enabled"] is False


def test_review_workbench_falls_back_to_first_attention_lane() -> None:
    model = _payload(selected_lane_id="missing-lane")

    assert model["selected_lane_id"] == "duplicates"
    assert model["attention_lane_ids"] == ["duplicates", "people-review"]
    assert model["summary"]["attention_lane_count"] == 2
    assert model["summary"]["selected_lane_id"] == "duplicates"


def test_review_workbench_exposes_stable_lane_ids_for_qt_navigation() -> None:
    model = _payload()

    assert model["available_lane_ids"] == [
        "duplicates",
        "similar-images",
        "people-review",
        "decision-summary",
    ]
    assert model["toolbar"]["available_lane_ids"] == model["available_lane_ids"]
    assert model["summary"]["navigation_target_page_id"] == "run-history"
    assert model["capabilities"]["requires_pyside6"] is False
    assert model["capabilities"]["opens_window"] is False
