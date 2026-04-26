from media_manager.core.gui_review_checklist import build_check_item, build_review_checklist, people_review_apply_checklist


def test_review_checklist_counts_failed_items() -> None:
    checklist = build_review_checklist([
        build_check_item("a", "A", passed=True),
        build_check_item("b", "B", passed=False, severity="error"),
    ])

    assert checklist["ready"] is False
    assert checklist["failed_count"] == 1
    assert checklist["blocking_count"] == 1


def test_people_review_apply_checklist_requires_encodings_and_privacy() -> None:
    checklist = people_review_apply_checklist(ready_group_count=1, has_encodings=False, privacy_acknowledged=False)

    assert checklist["ready"] is False
    assert checklist["blocking_count"] == 2
