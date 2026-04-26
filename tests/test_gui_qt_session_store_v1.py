from media_manager.core.gui_qt_session_store import build_qt_session_state, read_qt_session_state, register_recent_item, write_qt_session_state


def test_session_state_dedupes_recent_items_and_roundtrips(tmp_path) -> None:
    session = build_qt_session_state(active_page_id="people-review", recent_people_bundles=["a", "b", "a"])
    assert session["recent"]["people_bundles"] == ["a", "b"]
    updated = register_recent_item(session, category="people_bundle", value="c")
    assert updated["recent"]["people_bundles"][:2] == ["c", "a"]
    path = tmp_path / "session.json"
    write_qt_session_state(path, updated)
    assert read_qt_session_state(path)["active_page_id"] == "people-review"
