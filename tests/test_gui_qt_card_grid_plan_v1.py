from media_manager.core.gui_qt_card_grid_plan import build_qt_card_grid_plan, summarize_card_grid


def test_card_grid_places_cards_by_density() -> None:
    plan = build_qt_card_grid_plan(
        [{"id": "a", "title": "A"}, {"id": "b", "title": "B"}, {"id": "c", "title": "C"}],
        density="spacious",
    )
    assert plan["columns"] == 2
    assert plan["placements"][2]["row"] == 1
    assert summarize_card_grid(plan)["visible_card_count"] == 3


def test_card_grid_marks_truncation() -> None:
    plan = build_qt_card_grid_plan([{"title": str(index)} for index in range(4)], max_cards=2)
    assert plan["truncated"] is True
    assert plan["visible_card_count"] == 2
