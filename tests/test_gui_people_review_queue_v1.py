from __future__ import annotations

from media_manager.core.gui_people_review_queue import build_people_review_queue


def test_people_review_queue_filters_and_sorts() -> None:
    queue = build_people_review_queue([
        {"group_id": "b", "display_label": "Beta", "status": "ready_to_apply", "face_count": 2},
        {"group_id": "a", "display_label": "Alpha", "status": "needs_name", "face_count": 1},
    ])

    assert [row["group_id"] for row in queue["groups"]] == ["a", "b"]


def test_people_review_queue_searches_label() -> None:
    queue = build_people_review_queue([
        {"group_id": "a", "display_label": "Alice", "status": "needs_review"},
        {"group_id": "b", "display_label": "Bob", "status": "needs_review"},
    ], query="ali")

    assert queue["returned_group_count"] == 1
    assert queue["groups"][0]["display_label"] == "Alice"
