from media_manager.core.gui_review_heatmap import build_people_review_heatmap


def test_review_heatmap_buckets_by_status_and_face_count() -> None:
    heatmap = build_people_review_heatmap([
        {"status": "needs_review", "face_count": 2},
        {"status": "needs_review", "face_count": 6},
        {"status": "ready_to_apply", "counts": {"face_count": 3}},
    ], bucket_size=5)

    assert heatmap["kind"] == "people_review_heatmap"
    assert heatmap["total_group_count"] == 3
    assert any(cell["status"] == "ready_to_apply" for cell in heatmap["cells"])
