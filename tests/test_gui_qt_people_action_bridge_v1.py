from media_manager.core.gui_qt_people_action_bridge import build_people_review_button_bar, people_button_to_session_intent


def test_people_button_bar_builds_safe_session_intents():
    page = {"selected_group_id": "g1", "editor": {"selected_group_id": "g1", "detail_actions": [{"id": "accept_group", "label": "Accept"}, {"id": "apply_ready_groups", "label": "Apply", "variant": "danger", "risk_level": "high"}]}}
    bar = build_people_review_button_bar(page)
    assert bar["enabled_button_count"] == 2
    intent = people_button_to_session_intent(bar["buttons"][1])
    assert intent["session_action"] == "review_apply_preview"
    assert intent["requires_confirmation"] is True
    assert intent["executes_immediately"] is False
