from __future__ import annotations

from media_manager.core.gui_people_review_editor_model import build_people_review_editor_state


def test_people_review_editor_prioritizes_groups_needing_names() -> None:
    page = {"groups": [
        {"group_id": "ready", "display_label": "Jane", "status": "ready_to_apply", "face_count": 2},
        {"group_id": "new", "display_label": "Unknown", "status": "needs_name", "face_count": 3},
    ]}
    state = build_people_review_editor_state(page)
    assert state["groups"][0]["group_id"] == "new"
    assert state["selected_group_id"] == "new"
    assert state["detail_actions"][0]["id"] == "accept_group"
