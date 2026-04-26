from media_manager.core.gui_search_model import apply_search, build_search_state, summarize_search


def test_apply_search_filters_nested_rows() -> None:
    rows = [{"title": "Jane Doe", "status": "ready"}, {"title": "Max", "meta": {"note": "Family"}}]
    assert apply_search(rows, query="family")[0]["title"] == "Max"


def test_search_state_and_summary_are_stable() -> None:
    state = build_search_state(query="  Jane   Doe  ", fields=["title"])
    assert state["normalized_query"] == "jane doe"
    summary = summarize_search(original_count=3, returned_count=1, query="Jane")
    assert summary["filtered_count"] == 2
