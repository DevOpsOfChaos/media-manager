from media_manager.core.gui_filter_bar import apply_status_filter, build_status_filter_bar


def test_status_filter_bar_counts_and_filters() -> None:
    rows = [{"status": "ready"}, {"status": "blocked"}, {"status": "ready"}]
    bar = build_status_filter_bar(rows, selected_id="ready")
    assert bar["selected_id"] == "ready"
    assert next(item for item in bar["options"] if item["id"] == "ready")["count"] == 2
    assert len(apply_status_filter(rows, selected_id="ready")) == 2
