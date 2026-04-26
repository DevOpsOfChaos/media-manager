from media_manager.core.gui_selection_model import build_selection_state, clear_selection, select_people_group, toggle_face_selection


def test_selection_state_dedupes_faces() -> None:
    state = build_selection_state(active_page_id="people-review", selected_group_id="g1", selected_face_ids=["f1", "f1", "f2"])
    assert state["selected_face_ids"] == ["f1", "f2"]
    assert state["selected_face_count"] == 2
    assert state["has_people_selection"] is True


def test_select_group_can_clear_faces() -> None:
    state = build_selection_state(selected_face_ids=["f1"])
    next_state = select_people_group(state, "g2")
    assert next_state["selected_group_id"] == "g2"
    assert next_state["selected_face_ids"] == []


def test_toggle_face_selection_multi() -> None:
    state = build_selection_state(active_page_id="people-review")
    state = toggle_face_selection(state, "f1")
    state = toggle_face_selection(state, "f2")
    assert state["selected_face_ids"] == ["f1", "f2"]
    state = toggle_face_selection(state, "f1")
    assert state["selected_face_ids"] == ["f2"]


def test_clear_selection_keeps_page() -> None:
    state = build_selection_state(active_page_id="profiles", selected_profile_id="p1")
    assert clear_selection(state)["active_page_id"] == "profiles"
