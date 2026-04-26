from media_manager.core.gui_bulk_review_operations import build_bulk_review_operation, operation_from_selection, summarize_bulk_operations


def test_bulk_operation_dedupes_faces_and_is_non_executing() -> None:
    op = build_bulk_review_operation("reject_selected", group_id="g1", face_ids=["f1", "f1", "f2"])
    assert op["face_ids"] == ["f1", "f2"]
    assert op["requires_confirmation"] is True
    assert op["executes_immediately"] is False
    assert op["valid"] is True


def test_rename_group_requires_name() -> None:
    assert build_bulk_review_operation("rename_group", group_id="g1")["valid"] is False
    assert build_bulk_review_operation("rename_group", group_id="g1", selected_name="Jane")["valid"] is True


def test_operation_from_selection() -> None:
    selection = {"selected_group_id": "g1", "selected_face_ids": ["f1"]}
    op = operation_from_selection("split_selected", selection, note="not same person")
    assert op["group_id"] == "g1"
    assert op["face_ids"] == ["f1"]


def test_summarize_bulk_operations() -> None:
    summary = summarize_bulk_operations([
        build_bulk_review_operation("accept_group", group_id="g1"),
        build_bulk_review_operation("rename_group", group_id="g2"),
    ])
    assert summary["operation_count"] == 2
    assert summary["valid_count"] == 1
