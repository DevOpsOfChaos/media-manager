from media_manager.core.gui_qt_asset_review_gallery import build_asset_review_gallery, build_asset_review_gallery_from_page
from media_manager.core.gui_qt_demo_workspace import build_demo_people_page
from media_manager.core.gui_qt_review_lane_model import build_review_lanes_from_page


def test_review_lanes_bucket_groups() -> None:
    lanes = build_review_lanes_from_page(build_demo_people_page())
    assert lanes["group_count"] == 3
    ready = next(lane for lane in lanes["lanes"] if lane["id"] == "ready_to_apply")
    assert ready["count"] == 1


def test_asset_gallery_marks_sensitive_assets() -> None:
    gallery = build_asset_review_gallery([
        {"id": "face-1", "path": "faces/1.jpg", "kind": "face_crop"},
        {"id": "image-1", "path": "photos/a.jpg", "sensitive": False},
    ], selected_id="face-1")
    assert gallery["card_count"] == 2
    assert gallery["sensitive_count"] == 1
    assert gallery["cards"][0]["selected"] is True
    assert build_asset_review_gallery_from_page({"detail": {"faces": [{"face_id": "f"}]}})["card_count"] == 1
