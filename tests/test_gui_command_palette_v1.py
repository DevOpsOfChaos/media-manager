from __future__ import annotations

from media_manager.core.gui_command_palette import build_command_palette


def test_command_palette_is_safe_and_bilingual() -> None:
    payload = build_command_palette(language="de", home_state={"people_review": {"ready_for_gui": True}})
    assert payload["title"] == "Befehlspalette"
    assert payload["enabled_count"] >= 1
    assert all(item["executes_filesystem_changes"] is False for item in payload["commands"])
