from media_manager.core.gui_qt_shell_composition import build_qt_shell_composition


def test_shell_composition_combines_navigation_content_and_help() -> None:
    shell = {
        "active_page_id": "dashboard",
        "language": "en",
        "navigation": [{"id": "dashboard"}, {"id": "people-review"}],
        "page": {"page_id": "dashboard", "kind": "dashboard_page", "hero": {"title": "Hello"}, "cards": []},
        "home_state": {"manifest_summary": {"command_count": 3}},
    }
    composition = build_qt_shell_composition(shell)
    assert composition["ready"] is True
    assert composition["screen_map"]["active_page_id"] == "dashboard"
    assert composition["content"]["section_count"] >= 2
    assert composition["about"]["command_count"] == 3
