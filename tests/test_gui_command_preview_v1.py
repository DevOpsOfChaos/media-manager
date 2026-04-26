from __future__ import annotations

from media_manager.core.gui_command_preview import build_command_preview, quote_command_part


def test_command_preview_quotes_and_marks_sensitive_flags() -> None:
    assert quote_command_part("C:/My Folder") == '"C:/My Folder"'
    payload = build_command_preview(["media-manager", "people", "scan", "--include-encodings"], risk_level="high")
    assert payload["requires_confirmation"] is True
    assert "--include-encodings" in payload["sensitive_flags"]
