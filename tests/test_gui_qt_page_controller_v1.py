from media_manager.core.gui_qt_page_controller import build_page_controller_state, plan_page_switch, apply_page_switch, normalize_page_id


def test_page_controller_normalizes_aliases_and_switches():
    shell = {"active_page_id": "people", "navigation": [{"id": "dashboard", "label": "Dashboard"}, {"id": "people-review", "label": "People"}]}
    state = build_page_controller_state(shell)
    assert state["active_page_id"] == "people-review"
    assert normalize_page_id("runs") == "run-history"
    plan = plan_page_switch(state, "dashboard")
    assert plan["allowed"] is True
    updated = apply_page_switch(state, plan)
    assert updated["active_page_id"] == "dashboard"
    assert updated["navigation"][0]["active"] is True
