from __future__ import annotations

from media_manager.core.gui_people_review_model import build_people_review_card_grid, build_people_review_detail_model


def test_people_review_card_grid_uses_primary_assets() -> None:
    page = {
        "groups": [{"group_id": "g1", "display_label": "Jane", "status": "needs_review", "face_count": 2, "included_faces": 2, "excluded_faces": 0, "primary_face_id": "f1"}],
        "asset_refs": [{"face_id": "f1", "file_ref": {"path": "face.jpg"}}],
    }
    grid = build_people_review_card_grid(page)
    assert grid["card_count"] == 1
    assert grid["cards"][0]["thumbnail_ref"]["path"] == "face.jpg"


def test_people_review_detail_selects_first_group() -> None:
    detail = build_people_review_detail_model({"groups": [{"group_id": "g1"}]})
    assert detail["selected_group_id"] == "g1"
