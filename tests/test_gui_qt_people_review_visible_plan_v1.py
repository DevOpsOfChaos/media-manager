from media_manager.core.gui_qt_people_review_visible_plan import build_qt_people_review_visible_plan


def test_people_review_visible_plan_prioritizes_review_groups() -> None:
    page = {
        "page_id": "people-review",
        "kind": "people_review_page",
        "groups": [
            {"group_id": "ready", "display_label": "Ready", "status": "ready_to_apply", "face_count": 2},
            {"group_id": "name", "display_label": "Needs name", "status": "needs_name", "face_count": 1},
        ],
        "detail": {"faces": [{"face_id": "f1", "path": "a.jpg"}]},
    }
    plan = build_qt_people_review_visible_plan(page)
    assert plan["sections"][0]["children"][0]["group_id"] == "name"
    assert plan["visible_face_count"] == 1
    assert plan["privacy_notice"]


def test_people_review_visible_plan_empty_bundle() -> None:
    plan = build_qt_people_review_visible_plan({"page_id": "people-review", "empty_state": {"title": "Open bundle"}})
    assert plan["group_count"] == 0
    assert plan["sections"][-1]["variant"] == "empty_state"
