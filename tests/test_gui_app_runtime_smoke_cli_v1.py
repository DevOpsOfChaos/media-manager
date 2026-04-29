from __future__ import annotations

import json

from media_manager.gui_app import main


def test_gui_app_runtime_smoke_json_prints_guarded_integration(capsys) -> None:
    assert main(["--runtime-smoke-json", "--active-page", "dashboard"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["kind"] == "guarded_qt_runtime_smoke_integration"
    assert payload["summary"]["ready_for_shell_route"] is True
    assert payload["summary"]["opens_window"] is False


def test_gui_app_runtime_smoke_summary_is_headless(capsys) -> None:
    assert main(["--runtime-smoke-summary", "--active-page", "dashboard"]) == 0

    out = capsys.readouterr().out
    assert "Guarded Qt Runtime Smoke integration" in out
    assert "Executes commands now: False" in out
