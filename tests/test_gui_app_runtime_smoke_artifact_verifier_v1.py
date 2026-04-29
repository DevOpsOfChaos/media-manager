from __future__ import annotations

import json
import sys

from media_manager.gui_app import main


def test_gui_app_runtime_smoke_artifacts_verify_accepts_generated_pack(tmp_path, capsys) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    assert main(["--runtime-smoke-artifacts-dir", str(out)]) == 0
    capsys.readouterr()

    assert main(["--runtime-smoke-artifacts-verify", str(out)]) == 0
    text = capsys.readouterr().out

    assert "Qt Runtime Smoke artifact verification" in text
    assert "OK: True" in text
    assert "Opens window now: False" in text


def test_gui_app_runtime_smoke_artifacts_verify_json_returns_report(tmp_path, capsys) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    assert main(["--runtime-smoke-artifacts-dir", str(out)]) == 0
    capsys.readouterr()

    assert main(["--runtime-smoke-artifacts-verify", str(out), "--runtime-smoke-artifacts-verify-json"]) == 0
    report = json.loads(capsys.readouterr().out)

    assert report["kind"] == "qt_runtime_smoke_local_artifact_pack_verification"
    assert report["ok"] is True
    assert report["summary"]["privacy_redaction_ok"] is True


def test_gui_app_runtime_smoke_artifacts_verify_returns_nonzero_for_missing_dir(tmp_path, capsys) -> None:
    missing = tmp_path / "missing-artifacts"

    assert main(["--runtime-smoke-artifacts-verify", str(missing)]) == 2
    text = capsys.readouterr().out

    assert "OK: False" in text
    assert "missing-directory" in text


def test_gui_app_runtime_smoke_artifacts_verify_does_not_import_pyside6(tmp_path, capsys) -> None:
    sys.modules.pop("PySide6", None)
    out = tmp_path / "runtime-smoke-artifacts"
    assert main(["--runtime-smoke-artifacts-dir", str(out)]) == 0
    capsys.readouterr()

    assert main(["--runtime-smoke-artifacts-verify", str(out)]) == 0

    assert "PySide6" not in sys.modules


def test_gui_app_runtime_smoke_artifacts_verify_writes_report_dir(tmp_path, capsys) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    report_dir = tmp_path / "verification-proof"
    assert main(["--runtime-smoke-artifacts-dir", str(out)]) == 0
    capsys.readouterr()

    assert main(
        [
            "--runtime-smoke-artifacts-verify",
            str(out),
            "--runtime-smoke-artifacts-verify-report-dir",
            str(report_dir),
        ]
    ) == 0
    text = capsys.readouterr().out

    assert "Verification report files: 2" in text
    assert (report_dir / "runtime-smoke-artifacts-verification.json").is_file()
    assert (report_dir / "runtime-smoke-artifacts-verification.txt").is_file()
