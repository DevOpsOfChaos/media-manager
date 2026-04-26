from __future__ import annotations

from media_manager.core.gui_people_review_actions import build_people_face_actions, build_people_group_actions


def test_group_actions_block_accept_until_named() -> None:
    state = build_people_group_actions({"group_id": "unknown-1", "status": "needs_name", "face_count": 2})

    accept = next(action for action in state["actions"] if action["id"] == "accept_group")
    assert accept["enabled"] is False
    assert "blocked_reason" in accept


def test_group_actions_enable_apply_for_ready_group() -> None:
    state = build_people_group_actions({"group_id": "person-1", "display_label": "Jane", "status": "ready_to_apply", "face_count": 3})

    apply = next(action for action in state["actions"] if action["id"] == "apply_ready_groups")
    assert apply["enabled"] is True
    assert apply["requires_confirmation"] is True


def test_face_actions_toggle_include_state() -> None:
    included = build_people_face_actions({"face_id": "face-1", "include": True, "path": "a.jpg"})
    excluded = build_people_face_actions({"face_id": "face-1", "include": False})

    assert next(action for action in included["actions"] if action["id"] == "exclude_face")["enabled"] is True
    assert next(action for action in included["actions"] if action["id"] == "include_face")["enabled"] is False
    assert next(action for action in excluded["actions"] if action["id"] == "include_face")["enabled"] is True
