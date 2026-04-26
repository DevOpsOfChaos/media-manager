from media_manager.core.gui_presenter_state import build_presenter_state


def test_presenter_state_combines_breadcrumb_search_filter_action() -> None:
    page = {"page_id": "people-review", "title": "People", "groups": [{"status": "ready", "display_label": "Jane"}], "query": "Jane"}
    state = build_presenter_state(page_model=page, actions=[{"id": "review", "label": "Review"}])
    assert state["page_id"] == "people-review"
    assert state["breadcrumbs"]["items"][-1]["label"] == "People review"
    assert state["search"]["active"] is True
    assert state["filters"]["option_count"] >= 2
