from media_manager.core.gui_dashboard_presenter import build_dashboard_presenter


def test_dashboard_presenter_exposes_hero_cards_and_action_bar() -> None:
    page = {"page_id": "dashboard", "title": "Dashboard", "hero": {"title": "Welcome"}, "cards": [{"id": "runs", "title": "Runs"}]}
    presenter = build_dashboard_presenter(page)
    assert presenter["kind"] == "dashboard_presenter"
    assert presenter["hero"]["title"] == "Welcome"
    assert presenter["card_count"] == 1
    assert presenter["action_bar"]["action_count"] >= 1
