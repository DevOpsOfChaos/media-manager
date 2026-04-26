from media_manager.core.gui_media_preview_grid import build_media_preview_grid


def test_media_preview_grid_filters_and_selects_cards() -> None:
    payload = {
        "assets": [
            {"face_id": "face-1", "status": "ok", "path": "photos/a.jpg", "matched_name": "Jane", "asset_relative_path": "faces/1.jpg"},
            {"face_id": "face-2", "status": "error", "path": "photos/b.jpg", "error": "missing"},
        ]
    }

    grid = build_media_preview_grid(payload, query="jane", selected_ids=["face-1"])

    assert grid["kind"] == "media_preview_grid"
    assert grid["card_count"] == 1
    assert grid["selected_count"] == 1
    assert grid["cards"][0]["title"] == "Jane"


def test_media_preview_grid_reports_empty_state() -> None:
    grid = build_media_preview_grid([], query="x")

    assert grid["returned_card_count"] == 0
    assert grid["empty_state"]
