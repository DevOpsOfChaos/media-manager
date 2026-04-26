from media_manager.core.gui_responsive_layout import build_responsive_grid, build_responsive_regions


def test_responsive_grid_places_items() -> None:
    grid = build_responsive_grid([{"id": "a"}, {"id": "b"}, {"id": "c"}], viewport={"width": 900})

    assert grid["item_count"] == 3
    assert grid["columns"] >= 1
    assert grid["placements"][0]["row"] == 0
    assert grid["placements"][0]["column"] == 0


def test_people_regions_adapt_for_compact_width() -> None:
    compact = build_responsive_regions("people-review", viewport={"width": 500})
    wide = build_responsive_regions("people-review", viewport={"width": 1400})

    assert "queue" in compact["regions"]
    assert "queue_sidebar" in wide["regions"]
