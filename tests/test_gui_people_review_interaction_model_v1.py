from __future__ import annotations

from media_manager.core.gui_people_review_interaction_model import build_people_review_interaction_model


def test_interaction_model_selects_group_and_face() -> None:
    page = {
        "manifest_status": "ok",
        "overview": {"group_count": 1, "face_count": 2, "ready_group_count": 1},
        "selected_group_id": "group-1",
        "groups": [{"group_id": "group-1", "display_label": "Jane", "status": "ready_to_apply", "face_count": 2}],
        "detail": {"faces": [{"face_id": "face-1", "include": True, "path": "a.jpg"}]},
    }

    model = build_people_review_interaction_model(page, language="de")

    assert model["selected_group_id"] == "group-1"
    assert model["selected_face_id"] == "face-1"
    assert model["can_apply"] is True
    assert model["timeline"]["next_stage_id"] == "apply_preview"
    assert model["dialogs"][0]["type"] == "privacy"


def test_interaction_model_is_safe_for_empty_page() -> None:
    model = build_people_review_interaction_model({})

    assert model["selected_group_id"] is None
    assert model["group_actions"]["enabled_action_count"] == 0
    assert model["panel_state"]["visible_panel_count"] == 3
