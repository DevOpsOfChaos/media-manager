from __future__ import annotations

from media_manager.core.gui_page_contracts import (
    build_gui_navigation_state,
    build_gui_page_catalog,
    page_ids_for_commands,
    validate_gui_page_id,
)


def test_gui_page_catalog_includes_people_review_contract() -> None:
    catalog = build_gui_page_catalog()
    pages = {page["page_id"]: page for page in catalog["pages"]}

    assert catalog["kind"] == "gui_page_catalog"
    assert "people-review" in pages
    assert pages["people-review"]["risk_level"] == "sensitive"
    assert "bundle_manifest.json" in pages["people-review"]["required_artifacts"]
    assert "people-catalog" in pages


def test_gui_navigation_falls_back_to_dashboard_for_unknown_page() -> None:
    navigation = build_gui_navigation_state("does-not-exist")

    assert navigation["active_page_id"] == "dashboard"
    assert any(item["page_id"] == "dashboard" and item["active"] is True for item in navigation["items"])


def test_gui_page_ids_can_be_discovered_by_command() -> None:
    assert validate_gui_page_id("people-review") is True
    assert "people-review" in page_ids_for_commands(["people"])
    assert "settings-doctor" in page_ids_for_commands(["doctor"])
