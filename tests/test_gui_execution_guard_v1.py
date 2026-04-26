from media_manager.core.gui_execution_guard import guard_job_for_queue, inspect_command_safety


def test_guard_blocks_unconfirmed_risky_flags() -> None:
    safety = inspect_command_safety(["media-manager", "duplicates", "--apply", "--yes"])
    assert safety["blocked"] is True
    assert "confirmation_required" in safety["blocked_reasons"]
    assert "destructive_flags_blocked" in safety["blocked_reasons"]


def test_guard_allows_confirmed_non_destructive_preview() -> None:
    job = {"job_id": "j1", "action_id": "preview", "command_argv": ["media-manager", "people", "scan"]}
    guard = guard_job_for_queue(job)
    assert guard["safe_to_queue"] is True
    assert guard["status"] == "allowed"
