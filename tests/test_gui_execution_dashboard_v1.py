from media_manager.core.gui_command_queue import build_command_queue, enqueue_action
from media_manager.core.gui_execution_dashboard import build_execution_dashboard
from media_manager.core.gui_log_stream_model import append_log_entry, build_log_stream


def test_execution_dashboard_is_idle_by_default() -> None:
    dashboard = build_execution_dashboard()
    assert dashboard["status"] == "idle"
    assert dashboard["safe_execution_notice"]


def test_execution_dashboard_summarizes_queue_and_errors() -> None:
    queue = enqueue_action(build_command_queue(), action_id="preview", command_argv=["media-manager", "doctor"])
    logs = append_log_entry(build_log_stream(), "bad", level="error")
    dashboard = build_execution_dashboard(queue=queue, log_stream=logs)
    assert dashboard["requires_attention"] is True
    assert dashboard["queue"]["summary"]["status_summary"]["queued"] == 1
