from media_manager.core.gui_qt_image_card_adapter import build_qt_image_card, build_qt_image_card_grid


def test_image_card_grid_marks_sensitive_face_assets() -> None:
    assets = [{"face_id": "f1", "asset_path": "missing.jpg", "status": "ok"}, {"face_id": "f2", "path": "source.jpg"}]
    card = build_qt_image_card(assets[0], selected=True)
    assert card["selected"] is True
    assert card["sensitive"] is True
    grid = build_qt_image_card_grid(assets, selected_ids=["f2"], max_cards=1)
    assert grid["card_count"] == 1
    assert grid["truncated"] is True
    assert grid["sensitive_asset_count"] == 1
