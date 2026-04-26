from __future__ import annotations

from media_manager.core.gui_people_review_queue import build_people_review_queue


def test_people_review_queue_exposes_legacy_group_count_for_empty_queue() -> None:
    queue = build_people_review_queue([])

    assert queue["group_count"] == 0
    assert queue["total_group_count"] == 0
    assert queue["returned_group_count"] == 0


def test_people_review_queue_group_count_tracks_filtered_total_before_limit() -> None:
    queue = build_people_review_queue(
        [
            {"group_id": "a", "display_label": "Alice", "status": "needs_review"},
            {"group_id": "b", "display_label": "Bob", "status": "needs_review"},
        ],
        query="b",
        limit=1,
    )

    assert queue["group_count"] == 1
    assert queue["total_group_count"] == 1
    assert queue["returned_group_count"] == 1
    assert queue["groups"][0]["group_id"] == "b"
