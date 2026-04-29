from __future__ import annotations

import sys

from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import (
    summarize_guarded_qt_runtime_smoke_local_artifact_pack_verification,
    verify_guarded_qt_runtime_smoke_local_artifact_pack,
    write_guarded_qt_runtime_smoke_local_artifact_pack,
    write_guarded_qt_runtime_smoke_local_artifact_pack_verification_report,
)


def _results() -> list[dict[str, object]]:
    return [
        {"check_id": "launch-window", "passed": True, "evidence_path": "C:/local/smoke/window.png"},
        {"check_id": "navigation-visible", "passed": True},
        {"check_id": "no-auto-execution", "passed": True},
        {"check_id": "local-only", "passed": True},
    ]


def test_desktop_wrapper_verifies_local_artifact_pack_without_qt(tmp_path) -> None:
    sys.modules.pop("PySide6", None)
    out = tmp_path / "runtime-smoke-artifacts"
    write_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        str(out),
        results=_results(),
    )

    report = verify_guarded_qt_runtime_smoke_local_artifact_pack(str(out))

    assert report["ok"] is True
    assert report["summary"]["privacy_redaction_ok"] is True
    assert "PySide6" not in sys.modules


def test_desktop_wrapper_summarizes_local_artifact_pack_verification(tmp_path) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    write_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        str(out),
        results=_results(),
    )

    text = summarize_guarded_qt_runtime_smoke_local_artifact_pack_verification(str(out))

    assert "Qt Runtime Smoke artifact verification" in text
    assert "OK: True" in text
    assert "Executes commands now: False" in text


def test_desktop_wrapper_writes_verification_report_files(tmp_path) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    report_dir = tmp_path / "verification-proof"
    write_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        str(out),
        results=_results(),
    )

    report = write_guarded_qt_runtime_smoke_local_artifact_pack_verification_report(
        str(out),
        report_dir=str(report_dir),
    )

    assert report["ok"] is True
    assert report["summary"]["verification_report_file_count"] == 2
    assert (report_dir / "runtime-smoke-artifacts-verification.json").is_file()
