from __future__ import annotations

import json

from media_manager.gui_app import main


def test_gui_app_json_accepts_view_state_and_density(capsys) -> None:
    assert main(["--json", "--active-page", "people", "--density", "compact", "--language", "de"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["active_page_id"] == "people-review"
    assert payload["layout"]["density"] == "compact"
    assert payload["language"] == "de"


def test_gui_app_summary_mentions_interactive_navigation(capsys) -> None:
    assert main(["--summary", "--active-page", "dashboard"]) == 0
    out = capsys.readouterr().out

    assert "Interactive navigation" in out
