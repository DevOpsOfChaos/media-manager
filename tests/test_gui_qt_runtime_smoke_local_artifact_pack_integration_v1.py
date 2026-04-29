from __future__ import annotations

import json

from media_manager.core.gui_qt_runtime_smoke_result_payload import build_qt_runtime_smoke_result_payload_report
from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import (
    build_guarded_qt_runtime_smoke_plan,
    write_guarded_qt_runtime_smoke_local_artifact_pack,
)


def test_local_artifact_pack_includes_result_payload_report_when_supplied(tmp_path) -> None:
    result_report = build_qt_runtime_smoke_result_payload_report(
        {
            "results": [
                {"check_id": "launch-window", "passed": True, "evidence_path": "C:/local/smoke/window.png"},
                {"check_id": "navigation-visible", "passed": True},
                {"check_id": "no-auto-execution", "passed": True},
                {"check_id": "local-only", "passed": True},
            ]
        },
        source_path="C:/local/runtime-smoke-results.json",
    )
    out = tmp_path / "artifact-pack"

    pack = write_guarded_qt_runtime_smoke_local_artifact_pack(
        build_gui_shell_model(active_page_id="dashboard"),
        str(out),
        results=result_report["results"],
        result_payload_report=result_report,
    )

    assert pack["summary"]["written_file_count"] == 7
    manifest = json.loads((out / "runtime-smoke-artifacts-manifest.json").read_text(encoding="utf-8"))
    assert manifest["summary"]["has_result_payload_report"] is True


def test_local_artifact_pack_does_not_change_guarded_plan_status() -> None:
    result_report = build_qt_runtime_smoke_result_payload_report(
        {
            "results": [
                {"check_id": "launch-window", "passed": True},
                {"check_id": "navigation-visible", "passed": True},
                {"check_id": "no-auto-execution", "passed": True},
                {"check_id": "local-only", "passed": True},
            ]
        }
    )

    plan = build_guarded_qt_runtime_smoke_plan(
        build_gui_shell_model(active_page_id="dashboard"),
        results=result_report["results"],
    )

    assert plan["summary"]["accepted_after_results"] is True
    assert plan["summary"]["ready_to_start_manual_smoke"] is True
    assert plan["capabilities"]["opens_window"] is False
