from media_manager.core.gui_page_composer import compose_page_presenter, compose_shell_presenter


def test_compose_page_presenter_dispatches_dashboard() -> None:
    page = {"page_id": "dashboard", "title": "Dashboard", "cards": []}
    composed = compose_page_presenter(page)
    assert composed["page_id"] == "dashboard"
    assert composed["presenter"]["kind"] == "dashboard_presenter"


def test_compose_shell_presenter_wraps_active_page() -> None:
    shell = {"active_page_id": "people-review", "language": "en", "navigation": [], "page": {"page_id": "people-review", "groups": []}}
    composed = compose_shell_presenter(shell)
    assert composed["kind"] == "composed_shell"
    assert composed["page"]["page_id"] == "people-review"
