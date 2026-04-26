from media_manager.core.gui_qt_list_detail_plan import build_people_group_list_detail, build_qt_list_detail_plan


def test_list_detail_selects_requested_row() -> None:
    plan = build_qt_list_detail_plan([{"id": "a", "title": "A"}, {"id": "b", "title": "B"}], selected_id="b")
    assert plan["selected_id"] == "b"
    assert plan["detail"]["title"] == "B"


def test_people_group_list_detail_uses_group_ids() -> None:
    plan = build_people_group_list_detail({"groups": [{"group_id": "g1", "display_label": "Max"}], "selected_group_id": "g1"})
    assert plan["has_selection"] is True
