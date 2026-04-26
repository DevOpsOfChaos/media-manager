from __future__ import annotations

import json
from pathlib import Path

from media_manager.gui_app import main


def test_gui_app_json_is_headless_and_modern(tmp_path: Path, capsys) -> None:
    assert main(["--json", "--active-page", "dashboard", "--profile-dir", str(tmp_path / "profiles"), "--language", "de"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["application"]["id"] == "media-manager"
    assert payload["active_page_id"] == "dashboard"
    assert payload["language"] == "de"
    assert payload["capabilities"]["qt_shell"] is True
    assert payload["capabilities"]["tkinter_shell"] is False


def test_gui_app_summary_is_headless(capsys) -> None:
    assert main(["--summary", "--active-page", "profiles", "--theme", "modern-light"]) == 0
    output = capsys.readouterr().out

    assert "Media Manager" in output
    assert "Active page: profiles" in output
    assert "Theme: modern-light" in output


def test_gui_app_no_window_prints_summary(capsys) -> None:
    assert main(["--no-window", "--active-page", "run-history"]) == 0
    assert "Active page: run-history" in capsys.readouterr().out
