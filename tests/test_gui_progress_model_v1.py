from media_manager.core.gui_progress_model import build_progress_model, build_progress_stage


def test_progress_model_computes_percent_and_active() -> None:
    progress = build_progress_model([
        build_progress_stage("scan", "Scan", complete=True),
        build_progress_stage("review", "Review"),
        build_progress_stage("apply", "Apply"),
    ])

    assert progress["percent"] == 33
    assert progress["active_stage_id"] == "review"
    assert progress["blocked"] is False


def test_progress_model_reports_blocked() -> None:
    progress = build_progress_model([build_progress_stage("apply", "Apply", blocked=True)])

    assert progress["blocked"] is True
    assert progress["active_stage_id"] is None
