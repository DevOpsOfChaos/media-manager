from media_manager.core.gui_qt_command_palette_plan import build_qt_command_palette_plan, command_palette_row_to_intent


def test_command_palette_plan_filters_and_intent_is_safe():
    shell = {"command_palette": {"items": [{"id": "open_people", "label": "Open people", "page_id": "people-review"}, {"id": "settings", "label": "Settings"}]}}
    plan = build_qt_command_palette_plan(shell, query="people")
    assert plan["row_count"] == 1
    intent = command_palette_row_to_intent(plan["rows"][0])
    assert intent["page_id"] == "people-review"
    assert intent["executes_immediately"] is False
