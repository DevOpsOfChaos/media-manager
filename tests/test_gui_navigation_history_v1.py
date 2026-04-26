from media_manager.core.gui_navigation_history import build_navigation_history, go_back, go_forward, push_navigation


def test_navigation_history_push_back_forward() -> None:
    history = build_navigation_history("dashboard")
    history = push_navigation(history, "people-review")
    history = push_navigation(history, "profiles")

    assert history["current_page_id"] == "profiles"
    assert history["can_go_back"] is True

    history = go_back(history)
    assert history["current_page_id"] == "people-review"
    assert history["can_go_forward"] is True

    history = go_forward(history)
    assert history["current_page_id"] == "profiles"
