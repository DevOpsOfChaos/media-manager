from media_manager.core.gui_result_model import build_job_result, summarize_job_result


def test_successful_result() -> None:
    result = build_job_result(job_id="j1", exit_code=0, stdout="ok")
    assert result["status"] == "completed"
    assert summarize_job_result(result)["needs_attention"] is False


def test_failed_result_needs_attention() -> None:
    result = build_job_result(job_id="j1", exit_code=1, stderr="boom")
    assert result["status"] == "failed"
    assert summarize_job_result(result)["needs_attention"] is True
