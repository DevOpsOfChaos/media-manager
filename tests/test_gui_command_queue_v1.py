from media_manager.core.gui_command_queue import build_command_queue, dequeue_next_job, enqueue_action


def test_enqueue_safe_action() -> None:
    queue = enqueue_action(build_command_queue(), action_id="preview", command_argv=["media-manager", "doctor"])
    assert queue["summary"]["status_summary"]["queued"] == 1
    assert dequeue_next_job(queue)["has_job"] is True


def test_enqueue_risky_action_is_blocked_without_confirmation() -> None:
    queue = enqueue_action(build_command_queue(), action_id="apply", command_argv=["media-manager", "duplicates", "--apply", "--yes"], risk_level="destructive")
    assert queue["summary"]["status_summary"]["blocked"] == 1
    assert queue["last_guard"]["safe_to_queue"] is False
