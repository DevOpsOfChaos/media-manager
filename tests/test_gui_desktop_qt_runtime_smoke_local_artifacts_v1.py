from __future__ import annotations

import json
import sys

from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import (
    build_guarded_qt_runtime_smoke_local_artifact_pack,
    summarize_guarded_qt_runtime_smoke_local_artifact_pack,
    write_guarded_qt_runtime_smoke_local_artifact_pack,
)


def _passing_results() -> list[dict[str, object]]:
    return [
        {"check_id": "launch-window", "passed": True, "evidence_path": "C:/local/smoke/window.png"},
        {"check_id": "navigation-visible", "passed": True},
        {"check_id": "no-auto-execution", "passed": True},
        {"check_id": "local-only", "passed": True},
    ]


def test_desktop_wrapper_builds_local_artifact_pack_without_qt() -> None:
    sys.modules.pop("PySide6", None)
    pack = build_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        results=_passing_results(),
        reviewer="manual-operator",
    )
    assert pack["summary"]["accepted_after_results"] is True
    assert pack["summary"]["opens_window"] is False
    assert "PySide6" not in sys.modules


def test_desktop_wrapper_summarizes_local_artifact_pack() -> None:
    text = summarize_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        results=_passing_results(),
    )
    assert "Qt Runtime Smoke local artifacts" in text
    assert "Accepted after results: True" in text


def test_desktop_wrapper_writes_local_artifact_pack(tmp_path) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    pack = write_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        str(out),
        results=_passing_results(),
    )
    export = json.loads((out / "runtime-smoke-shareable-export.json").read_text(encoding="utf-8"))
    assert pack["summary"]["written_file_count"] == 6
    assert export["privacy"]["evidence_paths_redacted"] is True
    assert "evidence_path" not in export["session"]["results"][0]
