from __future__ import annotations

from media_manager.gui_desktop_qt import qt_install_guidance, shell_model_to_pretty_json


def test_qt_install_guidance_mentions_gui_extra() -> None:
    assert ".[gui]" in qt_install_guidance()


def test_shell_model_pretty_json_is_stable() -> None:
    text = shell_model_to_pretty_json({"b": 1})

    assert '"b": 1' in text
