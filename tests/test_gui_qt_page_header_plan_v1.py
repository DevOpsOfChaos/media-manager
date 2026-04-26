from media_manager.core.gui_qt_page_header_plan import build_qt_page_header_plan, header_has_actions


def test_header_plan_keeps_primary_action() -> None:
    plan = build_qt_page_header_plan(
        {"page_id": "dashboard", "title": "Dashboard"},
        actions=[{"id": "open", "label": "Open", "bucket": "primary"}],
    )
    assert plan["page_id"] == "dashboard"
    assert plan["primary_action"]["id"] == "open"
    assert header_has_actions(plan)
