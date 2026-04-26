from media_manager.core.gui_qt_execution_bridge import build_execution_control_panel, execution_control_to_intent, build_log_table_rows


def test_execution_bridge_controls_and_logs():
    dashboard = {"monitor": {"status": "queued"}, "queue": {"queued_count": 2}, "history": {"finished_count": 1}, "logs": {"entries": [{"level": "info", "message": "hello"}]}}
    panel = build_execution_control_panel(dashboard)
    assert panel["enabled_control_count"] == 2
    intent = execution_control_to_intent(panel["controls"][0])
    assert intent["executes_immediately"] is False
    assert build_log_table_rows(dashboard)[0]["message"] == "hello"
