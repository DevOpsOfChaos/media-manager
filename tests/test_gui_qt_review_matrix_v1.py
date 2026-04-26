from media_manager.core.gui_qt_review_matrix import build_qt_review_matrix


def test_review_matrix_counts_attention_groups() -> None:
    matrix = build_qt_review_matrix([{"group_id": "a", "status": "needs_name"}, {"group_id": "b", "status": "ready_to_apply"}])
    assert matrix["group_count"] == 2
    assert matrix["attention_count"] == 1
