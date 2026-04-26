from media_manager.core.gui_event_bus import build_gui_event
from media_manager.core.gui_state_reducer import apply_gui_events, reduce_gui_state


def test_reduce_gui_state_handles_navigation_and_selection() -> None:
    state = reduce_gui_state({}, build_gui_event("navigate", payload={"page_id": "people-review"}))
    state = reduce_gui_state(state, build_gui_event("people.group.select", payload={"group_id": "g1", "face_id": "f1"}))

    assert state["active_page_id"] == "people-review"
    assert state["selected_group_id"] == "g1"
    assert state["selected_face_id"] == "f1"


def test_apply_gui_events_adds_count() -> None:
    result = apply_gui_events({}, [build_gui_event("search.set", payload={"query": "Jane"})])

    assert result["query"] == "Jane"
    assert result["applied_event_count"] == 1
