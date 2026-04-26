from media_manager.core.gui_task_cards import build_task_card, task_cards_from_home_state


def test_task_card_is_stable_dict() -> None:
    card = build_task_card("people", "People", kind="people_review", status="ready", metrics={"groups": 2})

    assert card["kind"] == "task_card"
    assert card["metrics"]["groups"] == 2


def test_task_cards_from_home_state_summarizes_people() -> None:
    state = {
        "profiles": {"summary": {"profile_count": 1, "valid_count": 1}},
        "runs": {"summary": {"run_count": 3, "error_count": 1}},
        "people_review": {"ready_for_gui": True, "summary": {"group_count": 2, "face_count": 5}},
    }
    cards = task_cards_from_home_state(state)

    assert cards["card_count"] == 3
    assert cards["ready_count"] == 3
    assert next(card for card in cards["cards"] if card["card_id"] == "people")["metrics"]["faces"] == 5
