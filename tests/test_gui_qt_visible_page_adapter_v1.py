from media_manager.core.gui_qt_visible_page_adapter import build_qt_visible_page_plan, visible_page_plan_summary


def test_visible_page_adapter_dispatches_dashboard() -> None:
    plan = build_qt_visible_page_plan({"page_id": "dashboard", "kind": "dashboard_page", "title": "Dashboard", "cards": []})
    assert plan["body"]["kind"] == "qt_dashboard_visible_plan"
    assert visible_page_plan_summary(plan)["ready_for_qt"] is True


def test_visible_page_adapter_dispatches_table() -> None:
    plan = build_qt_visible_page_plan({"page_id": "runs", "kind": "table_page", "columns": ["id"], "rows": [{"id": "r1"}]})
    assert plan["body"]["kind"] == "qt_table_visible_plan"
    assert plan["body"]["visible_row_count"] == 1
