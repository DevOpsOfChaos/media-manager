from media_manager.core.gui_cancellation_model import apply_cancellation_marker, build_cancellation_request


def test_running_job_requires_cancel_confirmation() -> None:
    req = build_cancellation_request({"job_id": "j1", "status": "running"})
    assert req["can_cancel"] is True
    assert req["requires_confirmation"] is True
    assert req["executes_immediately"] is False


def test_completed_job_cannot_cancel() -> None:
    req = build_cancellation_request({"job_id": "j1", "status": "completed"})
    assert req["can_cancel"] is False
    assert req["blocked_reason"] == "job_is_not_cancellable"


def test_apply_cancellation_marker() -> None:
    job = apply_cancellation_marker({"job_id": "j1", "status": "queued"})
    assert job["status"] == "cancelled"
