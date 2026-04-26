from media_manager.core.gui_review_checklist import people_review_apply_checklist
from media_manager.core.gui_workflow_board import build_workflow_board, build_workflow_card
from media_manager.core.gui_workflow_summary import summarize_gui_workflow


def test_workflow_summary_combines_board_and_checklist() -> None:
    board = build_workflow_board([build_workflow_card("a", "A", status="blocked")])
    checklist = people_review_apply_checklist(ready_group_count=1, has_encodings=True, privacy_acknowledged=True)
    summary = summarize_gui_workflow(board=board, checklist=checklist, insights={"warning_count": 1, "next_action_id": "open"})

    assert summary["ready"] is False
    assert summary["blocked_count"] == 1
    assert summary["warning_count"] == 1
    assert summary["next_action_id"] == "open"
