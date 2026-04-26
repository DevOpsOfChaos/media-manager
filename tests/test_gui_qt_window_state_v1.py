from media_manager.core.gui_qt_window_state import build_qt_window_state, update_window_state, clamp_window_size


def test_window_state_clamps_and_updates():
    shell = {"window": {"title": "Media Manager", "width": 100, "height": 100}}
    state = build_qt_window_state(shell)
    assert state["width"] >= 1000
    assert clamp_window_size(99999, 99999)["width"] == 3840
    updated = update_window_state(state, width=1600, height=900, maximized=True)
    assert updated["width"] == 1600
    assert updated["maximized"] is True
