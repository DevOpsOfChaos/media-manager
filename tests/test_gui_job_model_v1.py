from media_manager.core.gui_job_model import build_gui_job, summarize_jobs, transition_gui_job


def test_job_requires_confirmation_for_destructive_risk() -> None:
    job = build_gui_job(action_id="apply_duplicate_cleanup", command_argv=["media-manager", "duplicates", "--apply", "--yes"], risk_level="destructive")
    assert job["requires_confirmation"] is True
    assert job["executes_immediately"] is False


def test_job_transition_and_summary() -> None:
    job = build_gui_job(action_id="preview", command_argv=["media-manager", "people", "scan"])
    running = transition_gui_job(job, "running")
    summary = summarize_jobs([running])
    assert running["status"] == "running"
    assert summary["running_count"] == 1
