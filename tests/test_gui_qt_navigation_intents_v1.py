from media_manager.core.gui_qt_navigation_intents import (
    build_qt_history_intent,
    build_qt_navigation_intent,
    build_qt_reload_intent,
    navigation_intent_from_action,
    normalize_qt_page_id,
)


def test_navigation_intents_are_safe_and_alias_pages() -> None:
    assert normalize_qt_page_id("people") == "people-review"
    intent = build_qt_navigation_intent("runs", source_page_id="dashboard")
    assert intent["target_page_id"] == "run-history"
    assert intent["executes_immediately"] is False
    assert intent["requires_confirmation"] is False


def test_reload_and_history_intents_are_safe() -> None:
    reload_intent = build_qt_reload_intent(page_id="people")
    back = build_qt_history_intent("back", current_page_id="people")
    assert reload_intent["target_page_id"] == "people-review"
    assert back["action"] == "back"
    assert back["executes_immediately"] is False


def test_navigation_intent_from_action_handles_unknown_actions() -> None:
    known = navigation_intent_from_action({"id": "open_people", "page_id": "people"})
    unknown = navigation_intent_from_action({"id": "explode"})
    assert known["kind"] == "qt_navigation_intent"
    assert known["target_page_id"] == "people-review"
    assert unknown["kind"] == "qt_unknown_intent"
    assert unknown["executes_immediately"] is False
