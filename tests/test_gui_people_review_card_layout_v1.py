from media_manager.core.gui_people_review_card_layout import build_people_face_card_layout, build_people_group_strip


def test_people_group_strip_builds_responsive_grid() -> None:
    page = {"selected_group_id": "g1", "groups": [{"group_id": "g1", "display_label": "Jane", "status": "needs_review", "face_count": 3}]}

    strip = build_people_group_strip(page, viewport={"width": 1200})

    assert strip["group_count"] == 1
    assert strip["grid"]["placements"][0]["item"]["selected"] is True


def test_people_face_card_layout_marks_sensitive() -> None:
    page = {"asset_refs": [{"face_id": "f1", "path": "face.jpg", "status": "ok"}]}

    layout = build_people_face_card_layout(page)

    assert layout["face_count"] == 1
    assert layout["grid"]["placements"][0]["item"]["sensitive"] is True
