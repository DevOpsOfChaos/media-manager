from media_manager.core.gui_keyboard_shortcuts import build_keyboard_shortcuts, detect_shortcut_conflicts


def test_keyboard_shortcuts_include_command_palette() -> None:
    payload = build_keyboard_shortcuts()

    assert payload["kind"] == "keyboard_shortcuts"
    assert any(item["action_id"] == "open_command_palette" for item in payload["shortcuts"])


def test_keyboard_shortcut_conflicts_are_detected() -> None:
    conflicts = detect_shortcut_conflicts([
        {"action_id": "a", "keys": "Ctrl+X", "scope": "global"},
        {"action_id": "b", "keys": "Ctrl+X", "scope": "global"},
    ])

    assert conflicts[0]["action_ids"] == ["a", "b"]
