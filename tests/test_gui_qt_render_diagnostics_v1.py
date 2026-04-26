from media_manager.core.gui_qt_render_diagnostics import build_qt_render_diagnostics


def test_render_diagnostics_report_missing_page_plan() -> None:
    diagnostics = build_qt_render_diagnostics(desktop_plan={"kind": "desktop"}, widget_tree={"children": []})
    assert diagnostics["valid"] is False
    assert diagnostics["problem_count"] == 1
    assert diagnostics["warning_count"] == 1


def test_render_diagnostics_accept_valid_minimal_plan() -> None:
    diagnostics = build_qt_render_diagnostics(desktop_plan={"page_plan": {"page_id": "dashboard"}}, widget_tree={"children": [{"id": "x"}]})
    assert diagnostics["valid"] is True
