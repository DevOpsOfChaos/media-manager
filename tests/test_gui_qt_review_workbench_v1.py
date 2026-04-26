from media_manager.core.gui_qt_pending_changes import build_pending_change
from media_manager.core.gui_qt_review_workbench import build_qt_review_workbench


def test_review_workbench_composes_pending_save_guard_and_flow() -> None:
    page = {"page_id": "people-review", "queue": {"groups": [{"group_id": "g1", "status": "ready_to_apply"}]}}
    workbench = build_qt_review_workbench(
        page_model=page,
        workspace_path="people-review-workflow.json",
        pending_changes=[build_pending_change("rename_group", target_id="g1", payload={"name": "Alice"})],
    )
    assert workbench["kind"] == "qt_review_workbench"
    assert workbench["pending_summary"]["pending_count"] == 1
    assert workbench["apply_preview"]["safe_to_apply"] is True
    assert workbench["flow"]["step_count"] == 5
    assert workbench["executes_immediately"] is False


def test_review_workbench_blocks_high_risk_pending_apply() -> None:
    page = {"page_id": "people-review", "queue": {"groups": [{"group_id": "g1", "status": "ready_to_apply"}]}}
    workbench = build_qt_review_workbench(
        page_model=page,
        workspace_path="people-review-workflow.json",
        pending_changes=[build_pending_change("apply_ready_groups", target_id="catalog", target_type="catalog")],
    )
    assert workbench["apply_preview"]["safe_to_apply"] is False
    assert workbench["guard"]["problem_count"] >= 1
