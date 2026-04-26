from media_manager.core.gui_people_review_renderer import build_people_review_render_spec


def test_people_review_renderer_handles_empty_and_groups() -> None:
    empty = build_people_review_render_spec({"page_id": "people-review", "groups": []})
    assert empty["summary"]["group_count"] == 0

    spec = build_people_review_render_spec({
        "page_id": "people-review",
        "groups": [
            {"group_id": "g1", "display_label": "Jane", "status": "needs_review", "face_count": 1, "faces": [{"face_id": "f1", "path": "a.jpg"}]},
        ],
        "asset_refs": [{"face_id": "f1", "path": "assets/f1.jpg"}],
    })
    assert spec["selected_group_id"] == "g1"
    assert spec["summary"]["group_count"] == 1
    assert spec["summary"]["selected_face_widget_count"] == 1
