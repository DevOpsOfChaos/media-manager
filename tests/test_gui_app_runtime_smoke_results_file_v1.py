from __future__ import annotations

import json
import sys

import pytest

from media_manager.gui_app import main


def _write_results_file(tmp_path, rows: list[dict[str, object]] | None = None):
    path = tmp_path / "runtime-smoke-results.json"
    path.write_text(
        json.dumps(
            {
                "results": rows
                or [
                    {"check_id": "launch-window", "passed": True, "note": "Opened cleanly."},
                    {"check_id": "navigation-visible", "passed": True},
                    {"check_id": "no-auto-execution", "passed": True},
                    {"check_id": "local-only", "passed": True},
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def test_gui_app_runtime_smoke_results_summary_is_headless(tmp_path, capsys) -> None:
    path = _write_results_file(tmp_path)

    assert main(["--runtime-smoke-results-file", str(path), "--runtime-smoke-results-summary"]) == 0

    out = capsys.readouterr().out
    assert "Qt Runtime Smoke manual result payload" in out
    assert "Accepted: True" in out
    assert "Opens window now: False" in out
    assert "Executes commands now: False" in out


def test_gui_app_runtime_smoke_json_includes_manual_results_file(tmp_path, capsys) -> None:
    path = _write_results_file(tmp_path)

    assert main(["--runtime-smoke-results-file", str(path), "--runtime-smoke-json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["accepted_after_results"] is True
    assert payload["smoke_report"]["summary"]["evidence_complete"] is True
    assert payload["result_bundle"]["summary"]["accepted"] is True
    assert payload["capabilities"]["opens_window"] is False


def test_gui_app_runtime_smoke_active_page_model_uses_manual_results_file(tmp_path, capsys) -> None:
    path = _write_results_file(tmp_path)

    assert main(["--active-page", "runtime-smoke", "--runtime-smoke-results-file", str(path), "--json"]) == 0

    shell = json.loads(capsys.readouterr().out)
    assert shell["active_page_id"] == "runtime-smoke"
    assert shell["page"]["presenter"]["metrics"]["evidence_complete"] is True
    assert shell["runtime_smoke"]["summary"]["accepted_after_results"] is True
    assert shell["runtime_smoke"]["summary"]["opens_window"] is False


def test_gui_app_runtime_smoke_results_template_is_headless(capsys) -> None:
    assert main(["--runtime-smoke-results-template"]) == 0

    template = json.loads(capsys.readouterr().out)
    assert template["kind"] == "qt_runtime_smoke_result_payload_template"
    assert template["summary"]["result_count"] >= 4
    assert template["summary"]["opens_window"] is False
    assert all(row["passed"] is None for row in template["results"])


def test_gui_app_runtime_smoke_results_file_failure_does_not_import_pyside6(tmp_path, capsys) -> None:
    sys.modules.pop("PySide6", None)
    path = _write_results_file(tmp_path, [{"check_id": "launch-window", "required": True, "passed": False}])

    assert main(["--runtime-smoke-results-file", str(path), "--runtime-smoke-results-summary"]) == 0

    out = capsys.readouterr().out
    assert "Accepted: False" in out
    assert "PySide6" not in sys.modules


def test_gui_app_runtime_smoke_results_summary_requires_file() -> None:
    with pytest.raises(SystemExit):
        main(["--runtime-smoke-results-summary"])
