from media_manager.core.gui_qt_deep_link import deep_link_to_navigation_intent, parse_qt_deep_link


def test_deep_link_parses_page_alias_and_intent() -> None:
    link = parse_qt_deep_link("media-manager://people?page=people&query=max")
    assert link["valid"] is True
    assert link["page_id"] == "people-review"
    assert link["params"]["query"] == "max"
    intent = deep_link_to_navigation_intent(link)
    assert intent["page_id"] == "people-review"
    assert intent["executes_immediately"] is False


def test_deep_link_rejects_unknown_scheme() -> None:
    assert parse_qt_deep_link("https://example.test") ["valid"] is False
