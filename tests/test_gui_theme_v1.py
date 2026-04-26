from __future__ import annotations

from media_manager.core.gui_theme import build_qt_stylesheet, build_theme_payload, normalize_theme


def test_theme_payload_contains_tokens() -> None:
    payload = build_theme_payload("modern-light")
    assert payload["theme"] == "modern-light"
    assert "background" in payload["tokens"]


def test_qt_stylesheet_is_generated_without_qt_dependency() -> None:
    assert "QMainWindow" in build_qt_stylesheet("modern-dark")
    assert normalize_theme("missing") == "modern-dark"
