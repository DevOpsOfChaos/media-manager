from __future__ import annotations

import json

from media_manager import gui_app


def test_runtime_smoke_json_cli_reports_ready_page_before_manual_results(capsys) -> None:
    exit_code = gui_app.main(["--active-page", "runtime-smoke", "--runtime-smoke-json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["summary"]["ready_to_start_manual_smoke"] is True
    assert payload["summary"]["problem_count"] == 0
    assert payload["page_model"]["presenter"]["status"] == "ready"
    assert payload["page_model"]["summary"]["ready_to_start_manual_smoke"] is True
    assert payload["smoke_report"]["summary"]["ready_for_release_gate"] is False


def test_runtime_smoke_summary_cli_keeps_manual_ready_and_no_window(capsys) -> None:
    exit_code = gui_app.main(["--active-page", "runtime-smoke", "--runtime-smoke-summary"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Ready to start manual smoke: True" in captured.out
    assert "Problem count: 0" in captured.out
    assert "Opens window now: False" in captured.out
    assert "Executes commands now: False" in captured.out
