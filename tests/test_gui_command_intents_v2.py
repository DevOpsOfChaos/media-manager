from __future__ import annotations

from media_manager.core.gui_command_intents import build_command_intent, build_intent_queue, intent_from_action


def test_command_intent_never_executes_immediately_v2() -> None:
    intent = build_command_intent("apply_people_review", label="Apply", risk_level="high")

    assert intent["intent_id"] == "apply-people-review"
    assert intent["executes_immediately"] is False
    assert intent["requires_confirmation"] is True


def test_intent_from_action_maps_risky_people_apply_v2() -> None:
    intent = intent_from_action({"id": "apply_ready_groups", "label": "Apply", "risk_level": "high"})

    assert intent["intent_id"] == "apply-people-review"
    assert intent["requires_confirmation"] is True


def test_intent_queue_counts_confirmation_v2() -> None:
    queue = build_intent_queue([
        {"id": "open_profiles", "label": "Open", "page_id": "profiles"},
        {"id": "apply_ready_groups", "label": "Apply", "risk_level": "high"},
    ])

    assert queue["intent_count"] == 2
    assert queue["confirmation_required_count"] == 1
