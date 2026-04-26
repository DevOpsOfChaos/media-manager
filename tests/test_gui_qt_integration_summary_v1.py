from media_manager.core.gui_qt_integration_summary import build_qt_integration_summary


def test_integration_summary_combines_render_state() -> None:
    summary = build_qt_integration_summary(
        desktop_plan={"active_page_id": "dashboard", "page_plan": {"kind": "dashboard"}},
        factory_plan={"widget_count": 4, "unsupported_widget_count": 0},
        diagnostics={"valid": True, "problem_count": 0, "warning_count": 1},
    )
    assert summary["active_page_id"] == "dashboard"
    assert summary["valid"] is True
    assert summary["ready_for_manual_qt_smoke"] is True
