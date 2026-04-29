from __future__ import annotations

import json

from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import build_guarded_qt_runtime_smoke_plan
from media_manager.core.gui_qt_runtime_smoke_local_artifact_pack import (
    build_qt_runtime_smoke_local_artifact_pack,
    summarize_qt_runtime_smoke_local_artifact_pack,
    write_qt_runtime_smoke_local_artifact_pack,
)


def _passing_results() -> list[dict[str, object]]:
    return [
        {"check_id": "launch-window", "passed": True, "evidence_path": "C:/local/smoke/window.png"},
        {"check_id": "navigation-visible", "passed": True},
        {"check_id": "no-auto-execution", "passed": True},
        {"check_id": "local-only", "passed": True},
    ]


def _plan() -> dict[str, object]:
    return build_guarded_qt_runtime_smoke_plan(
        build_gui_shell_model(active_page_id="dashboard"),
        results=_passing_results(),
        reviewer="manual-operator",
    )


def test_local_artifact_pack_contains_plan_template_export_and_manifest() -> None:
    pack = build_qt_runtime_smoke_local_artifact_pack(_plan())
    payloads = pack["payloads"]
    assert pack["kind"] == "qt_runtime_smoke_local_artifact_pack"
    assert payloads["runtime-smoke-plan.json"]["kind"] == "guarded_qt_runtime_smoke_integration"
    assert payloads["runtime-smoke-results-template.json"]["kind"] == "qt_runtime_smoke_result_payload_template"
    assert payloads["runtime-smoke-shareable-export.json"]["kind"] == "qt_runtime_smoke_export_bundle"
    assert payloads["runtime-smoke-artifacts-manifest.json"]["summary"]["file_count"] == 6
    assert payloads["runtime-smoke-summary.txt"].startswith("Qt Runtime Smoke local artifact pack")


def test_local_artifact_pack_shareable_export_redacts_evidence_paths() -> None:
    pack = build_qt_runtime_smoke_local_artifact_pack(_plan())
    export = pack["payloads"]["runtime-smoke-shareable-export.json"]
    result = export["session"]["results"][0]
    assert "evidence_path" not in result
    assert result["has_evidence_path"] is True
    assert export["privacy"]["evidence_paths_redacted"] is True
    assert export["privacy"]["contains_face_crops"] is False
    assert export["privacy"]["contains_embeddings"] is False


def test_local_artifact_pack_summary_is_headless_and_local_only() -> None:
    pack = build_qt_runtime_smoke_local_artifact_pack(_plan())
    text = summarize_qt_runtime_smoke_local_artifact_pack(pack)
    assert "Qt Runtime Smoke local artifacts" in text
    assert "Opens window now: False" in text
    assert "Executes commands now: False" in text
    assert pack["capabilities"]["requires_pyside6"] is False
    assert pack["capabilities"]["local_only"] is True


def test_write_local_artifact_pack_creates_expected_files(tmp_path) -> None:
    out = tmp_path / "runtime-smoke-artifacts"
    pack = write_qt_runtime_smoke_local_artifact_pack(_plan(), out)
    assert pack["summary"]["written_file_count"] == 6
    for name in [
        "runtime-smoke-plan.json",
        "runtime-smoke-results-template.json",
        "runtime-smoke-shareable-export.json",
        "runtime-smoke-summary.txt",
        "README.txt",
        "runtime-smoke-artifacts-manifest.json",
    ]:
        assert (out / name).is_file()
    manifest = json.loads((out / "runtime-smoke-artifacts-manifest.json").read_text(encoding="utf-8"))
    assert manifest["output_dir"] == str(out)
    assert manifest["summary"]["written_file_count"] == 6
