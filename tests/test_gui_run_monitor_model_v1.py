from media_manager.core.gui_command_queue import build_command_queue, enqueue_action
from media_manager.core.gui_log_stream_model import append_log_entry, build_log_stream
from media_manager.core.gui_run_monitor_model import build_monitor_tabs, build_run_monitor_state


def test_monitor_state_detects_queued_jobs() -> None:
    queue = enqueue_action(build_command_queue(), action_id="preview", command_argv=["media-manager", "doctor"])
    monitor = build_run_monitor_state(queue=queue)
    assert monitor["status"] == "queued"
    assert monitor["can_start_next"] is True


def test_monitor_tabs_include_history() -> None:
    assert build_monitor_tabs()[-1]["id"] == "history"


def test_monitor_detects_log_attention() -> None:
    logs = append_log_entry(build_log_stream(), "bad", level="error")
    monitor = build_run_monitor_state(log_stream=logs)
    assert monitor["status"] == "attention"
