from media_manager.core.gui_workflow_board import build_workflow_board, build_workflow_card, column_for_status


def test_workflow_card_normalizes_status_and_column() -> None:
    card = build_workflow_card("people", "Review people", status="needs-name")

    assert card["status"] == "needs_name"
    assert card["column"] == "review"
    assert card["blocked"] is False
    assert column_for_status("ready_to_apply") == "ready"


def test_workflow_board_summarizes_cards() -> None:
    cards = [
        build_workflow_card("a", "A", status="ready_to_apply"),
        build_workflow_card("b", "B", status="blocked"),
        build_workflow_card("c", "C", status="needs_review"),
    ]
    board = build_workflow_board(cards)

    assert board["summary"] == {"card_count": 3, "ready_count": 1, "blocked_count": 1, "review_count": 1}
    assert [column["id"] for column in board["columns"]][:3] == ["todo", "in_progress", "review"]
