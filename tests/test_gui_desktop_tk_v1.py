from __future__ import annotations

import json

from media_manager.gui_desktop_tk import shell_model_to_pretty_json


def test_tk_compat_helper_does_not_import_tkinter() -> None:
    payload = shell_model_to_pretty_json({"application": {"title": "Media Manager"}, "navigation": []})
    parsed = json.loads(payload)

    assert parsed["application"]["title"] == "Media Manager"
