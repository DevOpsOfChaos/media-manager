from media_manager.core.gui_qt_selection_sync import apply_selection_event, sync_selection_with_available_groups
from media_manager.core.gui_qt_drawer_actions import apply_drawer_action, build_drawer_state, drawer_action


def test_selection_sync_tracks_people_group_and_missing_group() -> None:
    selected = apply_selection_event({}, {"type": "select_group", "group_id": "g1"})
    assert selected["page_id"] == "people-review"
    assert selected["selected_group_id"] == "g1"

    synced = sync_selection_with_available_groups(selected, [{"group_id": "g2"}])
    assert synced["selected_group_id"] is None
    assert synced["sync_warning"] == "selected_group_missing"


def test_drawer_actions_toggle_open_state() -> None:
    state = build_drawer_state()
    opened = apply_drawer_action(state, drawer_action("diagnostics", "toggle"))

    assert opened["open_drawers"] == ["diagnostics"]
    assert opened["open_count"] == 1
