from __future__ import annotations

import json
import sys
from pathlib import Path

from media_manager.gui_app import main as gui_main


def test_gui_app_ui_view_models_json_does_not_import_pyside(capsys) -> None:
    sys.modules.pop("PySide6", None)
    assert gui_main(["--ui-view-models-json", "--active-page", "dashboard"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "ui_app_service_view_models"
    assert payload["capabilities"]["requires_pyside6"] is False
    assert payload["capabilities"]["executes_commands"] is False
    assert "PySide6" not in sys.modules


def test_gui_app_ui_view_models_out_dir(tmp_path: Path, capsys) -> None:
    assert gui_main(["--ui-view-models-out-dir", str(tmp_path / "models"), "--active-page", "run-history"]) == 0
    text = capsys.readouterr().out
    assert "Media Manager UI app-service view models" in text
    assert (tmp_path / "models" / "decision-summary.json").exists()
