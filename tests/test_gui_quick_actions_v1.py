from media_manager.core.gui_quick_actions import build_quick_action, build_quick_actions_for_page


def test_quick_action_marks_high_risk_confirmation() -> None:
    action = build_quick_action("apply", "Apply", risk_level="high")

    assert action["requires_confirmation"] is True
    assert action["executes_immediately"] is not True if "executes_immediately" in action else True


def test_people_review_quick_actions_respect_ready_context() -> None:
    disabled = build_quick_actions_for_page("people-review", context={"has_ready_people_groups": False})
    enabled = build_quick_actions_for_page("people-review", context={"has_ready_people_groups": True})

    assert disabled["action_count"] == 3
    assert next(action for action in disabled["actions"] if action["id"] == "apply_ready")["enabled"] is False
    assert next(action for action in enabled["actions"] if action["id"] == "apply_ready")["enabled"] is True
