from __future__ import annotations

from media_manager.core.gui_theme import build_theme_payload


def test_theme_payload_keeps_tokens_alias_for_legacy_callers() -> None:
    payload = build_theme_payload("modern-light")

    assert payload["theme"] == "modern-light"
    assert "background" in payload["tokens"]
    assert payload["tokens"] == payload["palette"]
    assert payload["tokens"] is not payload["palette"]
