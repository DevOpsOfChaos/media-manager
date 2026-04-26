from media_manager.core.gui_pagination import build_pagination_state, clamp_page, page_summary_text


def test_clamp_page_bounds() -> None:
    assert clamp_page(99, total_items=12, page_size=5) == 3
    assert clamp_page(-4, total_items=12, page_size=5) == 1


def test_build_pagination_state_returns_slice() -> None:
    state = build_pagination_state(list(range(12)), page=2, page_size=5)
    assert state["items"] == [5, 6, 7, 8, 9]
    assert state["has_previous"] is True
    assert state["has_next"] is True
    assert page_summary_text(state) == "6-10 of 12"


def test_empty_pagination_is_safe() -> None:
    state = build_pagination_state([], page=3, page_size=0)
    assert state["page"] == 1
    assert state["items"] == []
    assert page_summary_text(state) == "0 items"
