from __future__ import annotations

from media_manager.core.gui_i18n import build_language_catalog, normalize_language, translate


def test_translate_supports_english_and_german() -> None:
    assert translate("nav.dashboard", language="en") == "Dashboard"
    assert translate("nav.dashboard", language="de") == "Übersicht"
    assert normalize_language("de-DE") == "de"


def test_language_catalog_contains_labels() -> None:
    payload = build_language_catalog("de")
    assert payload["language"] == "de"
    assert payload["labels"]["page.people-review.title"] == "Personenprüfung"
