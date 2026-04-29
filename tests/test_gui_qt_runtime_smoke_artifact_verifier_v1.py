from __future__ import annotations

import json
import sys

from media_manager.core.gui_qt_runtime_smoke_artifact_verifier import (
    summarize_qt_runtime_smoke_local_artifact_pack_verification,
    verify_qt_runtime_smoke_local_artifact_pack_dir,
    write_qt_runtime_smoke_local_artifact_pack_verification_report,
)
from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import write_guarded_qt_runtime_smoke_local_artifact_pack


def _results() -> list[dict[str, object]]:
    return [
        {"check_id": "launch-window", "passed": True, "evidence_path": "C:/local/smoke/window.png"},
        {"check_id": "navigation-visible", "passed": True},
        {"check_id": "no-auto-execution", "passed": True},
        {"check_id": "local-only", "passed": True},
    ]


def _write_pack(tmp_path):
    out = tmp_path / "runtime-smoke-artifacts"
    write_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        str(out),
        results=_results(),
        reviewer="manual-operator",
    )
    return out


def test_artifact_verifier_accepts_generated_pack(tmp_path) -> None:
    report = verify_qt_runtime_smoke_local_artifact_pack_dir(_write_pack(tmp_path))

    assert report["kind"] == "qt_runtime_smoke_local_artifact_pack_verification"
    assert report["ok"] is True
    assert report["summary"]["existing_file_count"] == 6
    assert report["summary"]["privacy_redaction_ok"] is True
    assert all(item["sha256"] for item in report["files"] if item["exists"])


def test_artifact_verifier_summarizes_success(tmp_path) -> None:
    text = summarize_qt_runtime_smoke_local_artifact_pack_verification(
        verify_qt_runtime_smoke_local_artifact_pack_dir(_write_pack(tmp_path))
    )

    assert "Qt Runtime Smoke artifact verification" in text
    assert "OK: True" in text
    assert "Privacy redaction OK: True" in text


def test_artifact_verifier_flags_missing_manifest(tmp_path) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    out.mkdir()

    report = verify_qt_runtime_smoke_local_artifact_pack_dir(out)

    assert report["ok"] is False
    assert any(problem["code"] == "missing-manifest" for problem in report["problems"])


def test_artifact_verifier_flags_shareable_export_evidence_path_leak(tmp_path) -> None:
    out = _write_pack(tmp_path)
    export_path = out / "runtime-smoke-shareable-export.json"
    export = json.loads(export_path.read_text(encoding="utf-8"))
    export["session"]["results"][0]["evidence_path"] = "C:/local/private/window.png"
    export_path.write_text(json.dumps(export), encoding="utf-8")

    report = verify_qt_runtime_smoke_local_artifact_pack_dir(out)

    assert report["ok"] is False
    assert any(problem["code"] == "export-evidence-path-leak" for problem in report["problems"])


def test_artifact_verifier_does_not_import_pyside6(tmp_path) -> None:
    sys.modules.pop("PySide6", None)

    report = verify_qt_runtime_smoke_local_artifact_pack_dir(_write_pack(tmp_path))

    assert report["capabilities"]["requires_pyside6"] is False
    assert report["capabilities"]["reads_evidence_files"] is False
    assert "PySide6" not in sys.modules


def test_artifact_verifier_writes_local_verification_report_files(tmp_path) -> None:
    out = _write_pack(tmp_path)
    report_dir = tmp_path / "verification-proof"

    report = write_qt_runtime_smoke_local_artifact_pack_verification_report(out, output_dir=report_dir)

    assert report["ok"] is True
    assert report["summary"]["verification_report_file_count"] == 2
    assert (report_dir / "runtime-smoke-artifacts-verification.json").is_file()
    assert (report_dir / "runtime-smoke-artifacts-verification.txt").is_file()
