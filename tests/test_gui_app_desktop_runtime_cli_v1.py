from __future__ import annotations

import json
import sys
from pathlib import Path

from media_manager.gui_app import main as gui_main


def test_gui_app_desktop_runtime_json_does_not_import_pyside(capsys) -> None:
    sys.modules.pop("PySide6", None)

    assert gui_main(["--desktop-runtime-json", "--active-page", "dashboard"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["kind"] == "gui_desktop_runtime_state"
    assert payload["readiness"]["ready"] is True
    assert payload["capabilities"]["requires_pyside6"] is False
    assert "PySide6" not in sys.modules


def test_gui_app_desktop_runtime_summary(capsys) -> None:
    assert gui_main(["--desktop-runtime-summary", "--active-page", "people-review"]) == 0
    text = capsys.readouterr().out

    assert "Media Manager desktop runtime state" in text
    assert "Active page: people-review" in text
    assert "Opens window: False" in text


def test_gui_app_desktop_runtime_out_dir(tmp_path: Path, capsys) -> None:
    assert gui_main(["--desktop-runtime-out-dir", str(tmp_path / "desktop"), "--active-page", "settings-doctor"]) == 0
    text = capsys.readouterr().out

    assert "Active page: settings" in text
    assert (tmp_path / "desktop" / "shell_model.json").exists()
    payload = json.loads((tmp_path / "desktop" / "desktop_runtime_state.json").read_text(encoding="utf-8"))
    assert payload["summary"]["page_kind"] == "settings_page"


def test_gui_app_desktop_runtime_can_build_runtime_smoke_page_without_window(capsys) -> None:
    assert gui_main(["--desktop-runtime-json", "--active-page", "runtime-smoke"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["summary"]["active_page_id"] == "runtime-smoke"
    assert payload["summary"]["page_kind"] == "qt_runtime_smoke_page_model"
    assert payload["capabilities"]["executes_commands"] is False
