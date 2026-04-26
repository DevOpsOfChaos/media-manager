from __future__ import annotations

from media_manager.core.gui_qt_people_review_page import build_qt_people_review_page_plan


def test_people_review_page_plan_orders_groups_and_selects_first() -> None:
    plan = build_qt_people_review_page_plan(
        {
            "page_id": "people-review",
            "title": "People",
            "groups": [
                {"group_id": "ready", "display_label": "Ready", "status": "ready_to_apply", "face_count": 4},
                {"group_id": "name", "display_label": "Needs Name", "status": "needs_name", "face_count": 1},
            ],
            "detail": {"title": "Detail", "faces": [{"face_id": "f1"}]},
        }
    )

    assert plan["layout"] == "people_review_master_detail"
    assert plan["selected_group_id"] == "name"
    group_list = next(item for item in plan["widgets"] if item["widget_type"] == "people_group_list")
    assert group_list["groups"][0]["group_id"] == "name"
    assert group_list["groups"][0]["selected"] is True
