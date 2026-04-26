from __future__ import annotations

from media_manager.core.gui_theme import build_qt_stylesheet, build_theme_payload


def test_theme_payload_has_modern_tokens() -> None:
    payload = build_theme_payload("modern-light")

    assert payload["schema_version"] == "1.1"
    assert payload["radius"]["lg"] == 20
    assert payload["typography"]["font_family"] == "Segoe UI"


def test_qt_stylesheet_has_new_objects() -> None:
    stylesheet = build_qt_stylesheet("modern-dark")

    assert "QFrame#Section" in stylesheet
    assert "QLabel#CardTitle" in stylesheet
    assert "QPushButton:checked" in stylesheet
