from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_app_services import main as app_services_main


def test_cli_app_services_ui_view_models_json(capsys) -> None:
    assert app_services_main(["ui-view-models", "--active-page", "dashboard", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "ui_app_service_view_models"
    assert payload["summary"]["view_model_count"] == 7
    assert payload["capabilities"]["opens_window"] is False


def test_cli_app_services_ui_view_models_out_dir(tmp_path: Path, capsys) -> None:
    assert app_services_main(["ui-view-models", "--out-dir", str(tmp_path / "models")]) == 0
    text = capsys.readouterr().out
    assert "Media Manager UI app-service view models" in text
    assert (tmp_path / "models" / "ui_app_service_view_models.json").exists()
    assert (tmp_path / "models" / "run-history.json").exists()
    assert (tmp_path / "models" / "review-workbench.json").exists()
