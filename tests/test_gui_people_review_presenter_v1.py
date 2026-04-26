from media_manager.core.gui_people_review_presenter import build_people_review_presenter


def test_people_review_presenter_selects_and_filters_group() -> None:
    page = {
        "page_id": "people-review",
        "title": "People",
        "overview": {"ready_group_count": 1},
        "groups": [
            {"group_id": "g1", "display_label": "Jane", "status": "ready_to_apply", "face_count": 3},
            {"group_id": "g2", "display_label": "Max", "status": "needs_name", "face_count": 1},
        ],
    }
    presenter = build_people_review_presenter(page, query="jane")
    assert presenter["master"]["group_count"] == 1
    assert presenter["detail"]["title"] == "Jane"
    assert presenter["action_bar"]["confirmation_count"] == 1
