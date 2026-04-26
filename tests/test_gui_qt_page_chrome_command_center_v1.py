from media_manager.core.gui_qt_command_center import build_command_center, command_center_to_intent
from media_manager.core.gui_qt_page_chrome import build_page_chrome
from media_manager.core.gui_qt_view_templates import get_view_template, validate_page_against_template


def test_page_chrome_and_template_are_safe() -> None:
    page = {"page_id": "people-review", "title": "People review", "groups": [], "actions": [{"id": "apply", "risk_level": "high", "requires_confirmation": True}]}
    chrome = build_page_chrome(page)
    assert chrome["page_id"] == "people-review"
    assert chrome["actions"]["confirmation_count"] == 1
    assert chrome["actions"]["actions"][0]["executes_immediately"] is False
    assert get_view_template("people")["page_id"] == "people-review"
    assert validate_page_against_template(page)["valid"] is True


def test_command_center_filters_and_returns_intents() -> None:
    center = build_command_center(query="people")
    assert center["row_count"] == 1
    intent = command_center_to_intent(center["rows"][0])
    assert intent["intent_type"] == "navigate"
    assert intent["target_page_id"] == "people-review"
    assert intent["executes_immediately"] is False
