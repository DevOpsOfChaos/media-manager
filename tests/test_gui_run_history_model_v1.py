from __future__ import annotations

from media_manager.core.gui_run_history_model import build_run_history_page_state


def test_run_history_state_builds_filterable_table() -> None:
    state = build_run_history_page_state({"runs": {"items": [{"run_id": "r1", "status": "ok"}]}})
    assert state["filters"]["filters"][0]["id"] == "all"
    assert state["table"]["row_count"] == 1
    assert state["table"]["rows"][0]["status_badge"]["tone"] == "success"
