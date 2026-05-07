from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main


def test_cli_app_services_desktop_runtime_json(capsys) -> None:
    exit_code = app_services_main(["desktop-runtime", "--active-page", "dashboard", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == "gui_desktop_runtime_state"
    assert payload["summary"]["active_page_id"] == "dashboard"
    assert payload["capabilities"]["opens_window"] is False


def test_cli_app_services_desktop_runtime_text(capsys) -> None:
    app_services_main(["desktop-runtime", "--active-page", "profiles"])
    text = capsys.readouterr().out

    assert "Media Manager desktop runtime state" in text
    assert "Active page: profiles" in text
    assert "Executes commands: False" in text


def test_cli_app_services_desktop_runtime_out_dir(tmp_path: Path, capsys) -> None:
    app_services_main(["desktop-runtime", "--active-page", "settings-doctor", "--out-dir", str(tmp_path / "runtime")])
    text = capsys.readouterr().out

    assert "Active page: settings" in text
    assert (tmp_path / "runtime" / "desktop_runtime_state.json").exists()
    payload = json.loads((tmp_path / "runtime" / "desktop_runtime_state.json").read_text(encoding="utf-8"))
    assert payload["summary"]["page_kind"] == "settings_page"


def test_cli_app_services_desktop_runtime_respects_out_json(tmp_path: Path, capsys) -> None:
    out = tmp_path / "state.json"
    app_services_main(["desktop-runtime", "--active-page", "run-history", "--out", str(out), "--json"])
    payload = json.loads(capsys.readouterr().out)
    written = json.loads(out.read_text(encoding="utf-8"))

    assert payload["summary"]["active_page_id"] == "run-history"
    assert written["summary"]["active_page_id"] == "run-history"
