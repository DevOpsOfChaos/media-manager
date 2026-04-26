from __future__ import annotations

import json

from media_manager.gui_desktop_qt import MissingQtDependencyError, qt_install_guidance, shell_model_to_pretty_json


def test_shell_model_to_pretty_json_does_not_require_qt() -> None:
    payload = shell_model_to_pretty_json({"application": {"title": "Media Manager"}, "navigation": []})
    parsed = json.loads(payload)

    assert parsed["application"]["title"] == "Media Manager"


def test_qt_install_guidance_mentions_gui_extra() -> None:
    assert ".[gui]" in qt_install_guidance()
    assert issubclass(MissingQtDependencyError, RuntimeError)
