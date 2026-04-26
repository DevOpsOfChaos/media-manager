from media_manager.core.gui_event_bus import append_gui_event, build_event_queue, build_gui_event


def test_event_queue_summarizes_types() -> None:
    event = build_gui_event("navigate", payload={"page_id": "dashboard"}, sequence=1)
    queue = build_event_queue([event])

    assert event["executes_immediately"] is False
    assert queue["event_count"] == 1
    assert queue["type_summary"] == {"navigate": 1}


def test_append_gui_event_returns_new_queue() -> None:
    queue = append_gui_event(build_event_queue(), build_gui_event("search.set", payload={"query": "max"}))

    assert queue["event_count"] == 1
