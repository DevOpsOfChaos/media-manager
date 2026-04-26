from media_manager.core.gui_qt_page_storyboard import build_page_storyboard, normalize_storyboard_page_id, storyboard_summary
from media_manager.core.gui_qt_people_review_dashboard import build_people_review_dashboard


def test_storyboard_normalizes_aliases_and_localizes() -> None:
    board = build_page_storyboard(["home", "people", "runs"], active_page_id="people", language="de")
    assert board["active_page_id"] == "people-review"
    assert board["scene_count"] == 3
    assert board["scenes"][1]["label"] == "Personenprüfung"
    assert normalize_storyboard_page_id("history") == "run-history"
    assert storyboard_summary(board)["routes"] == ["/dashboard", "/people-review", "/run-history"]


def test_people_review_dashboard_counts_attention_and_safe_apply() -> None:
    page = {
        "overview": {"face_count": 8},
        "queue": {"query": "max", "returned_group_count": 3},
        "groups": [
            {"group_id": "g1", "status": "needs_name"},
            {"group_id": "g2", "status": "needs_review"},
            {"group_id": "g3", "status": "ready_to_apply"},
        ],
    }
    dashboard = build_people_review_dashboard(page)
    assert dashboard["group_count"] == 3
    assert dashboard["attention_count"] == 2
    assert dashboard["safe_to_apply"] is False
    assert dashboard["status_counts"]["ready_to_apply"] == 1
