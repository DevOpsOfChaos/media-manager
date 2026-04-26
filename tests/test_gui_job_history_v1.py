from media_manager.core.gui_job_history import build_job_history, record_job_result
from media_manager.core.gui_job_model import build_gui_job, transition_gui_job


def test_job_history_summarizes_terminal_jobs() -> None:
    job = transition_gui_job(build_gui_job(action_id="preview"), "completed")
    history = build_job_history([job])
    assert history["terminal_count"] == 1
    assert history["summary"]["status_summary"]["completed"] == 1


def test_record_job_result_adds_job() -> None:
    job = transition_gui_job(build_gui_job(action_id="preview"), "failed")
    history = record_job_result(build_job_history(), job)
    assert history["job_count"] == 1
