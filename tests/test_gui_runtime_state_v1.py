from media_manager.core.gui_runtime_state import build_gui_runtime_state, summarize_runtime_state


def test_runtime_state_marks_safe_mode_and_ready() -> None:
    shell = {"active_page_id": "dashboard", "language": "de", "theme": {"theme": "modern-dark"}, "navigation": [1], "capabilities": {"executes_commands": False}}
    state = build_gui_runtime_state(shell, diagnostics={"blocking_count": 0})
    assert state["safe_mode"] is True
    assert state["ready"] is True
    assert "GUI runtime state" in summarize_runtime_state(state)
