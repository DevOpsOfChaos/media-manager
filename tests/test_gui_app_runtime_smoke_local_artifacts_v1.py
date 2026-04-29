from __future__ import annotations

import json
import sys

import pytest

from media_manager.gui_app import main


def _write_results_file(tmp_path):
    path = tmp_path / "runtime-smoke-results.json"
    path.write_text(
        json.dumps(
            {
                "results": [
                    {"check_id": "launch-window", "passed": True, "evidence_path": "C:/local/smoke/window.png"},
                    {"check_id": "navigation-visible", "passed": True},
                    {"check_id": "no-auto-execution", "passed": True},
                    {"check_id": "local-only", "passed": True},
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


def test_gui_app_runtime_smoke_artifacts_summary_is_headless(capsys) -> None:
    assert main(["--runtime-smoke-artifacts-summary"]) == 0
    out = capsys.readouterr().out
    assert "Qt Runtime Smoke local artifacts" in out
    assert "Opens window now: False" in out
    assert "Executes commands now: False" in out


def test_gui_app_runtime_smoke_artifacts_dir_writes_files(tmp_path, capsys) -> None:
    out_dir = tmp_path / "artifact-pack"
    assert main(["--runtime-smoke-artifacts-dir", str(out_dir)]) == 0
    out = capsys.readouterr().out
    assert "Written files: 6" in out
    for name in [
        "runtime-smoke-plan.json",
        "runtime-smoke-results-template.json",
        "runtime-smoke-shareable-export.json",
        "runtime-smoke-artifacts-manifest.json",
    ]:
        assert (out_dir / name).is_file()


def test_gui_app_runtime_smoke_artifacts_dir_uses_result_file(tmp_path, capsys) -> None:
    results_file = _write_results_file(tmp_path)
    out_dir = tmp_path / "artifact-pack"
    assert main(["--runtime-smoke-results-file", str(results_file), "--runtime-smoke-artifacts-dir", str(out_dir)]) == 0
    out = capsys.readouterr().out
    assert "Written files: 7" in out
    manifest = json.loads((out_dir / "runtime-smoke-artifacts-manifest.json").read_text(encoding="utf-8"))
    result_report = json.loads((out_dir / "runtime-smoke-result-payload-report.json").read_text(encoding="utf-8"))
    export = json.loads((out_dir / "runtime-smoke-shareable-export.json").read_text(encoding="utf-8"))
    assert manifest["summary"]["has_result_payload_report"] is True
    assert result_report["accepted"] is True
    assert export["session"]["results"][0]["has_evidence_path"] is True
    assert "evidence_path" not in export["session"]["results"][0]


def test_gui_app_runtime_smoke_artifacts_do_not_import_pyside6(tmp_path) -> None:
    sys.modules.pop("PySide6", None)
    assert main(["--runtime-smoke-artifacts-dir", str(tmp_path / "artifact-pack")]) == 0
    assert "PySide6" not in sys.modules


def test_gui_app_runtime_smoke_artifacts_dir_rejects_file_target(tmp_path) -> None:
    target = tmp_path / "not-a-dir"
    target.write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["--runtime-smoke-artifacts-dir", str(target)])
