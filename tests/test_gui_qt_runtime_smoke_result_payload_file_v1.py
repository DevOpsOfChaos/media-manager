from __future__ import annotations

import json
import sys

from media_manager.core.gui_qt_runtime_smoke_result_payload import (
    build_qt_runtime_smoke_result_collector_template,
    build_qt_runtime_smoke_result_payload_report,
    load_qt_runtime_smoke_result_payload_file,
)
from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_shell_model import build_gui_shell_model


def _passing_results() -> list[dict[str, object]]:
    return [
        {"check_id": "launch-window", "passed": True, "note": "Opened cleanly."},
        {"check_id": "navigation-visible", "passed": True},
        {"check_id": "no-auto-execution", "passed": True},
        {"check_id": "local-only", "passed": True},
    ]


def test_runtime_smoke_result_payload_file_extracts_results_object(tmp_path) -> None:
    path = tmp_path / "runtime-smoke-results.json"
    path.write_text(json.dumps({"results": _passing_results()}), encoding="utf-8")

    report = load_qt_runtime_smoke_result_payload_file(path)

    assert report["kind"] == "qt_runtime_smoke_result_payload_report"
    assert report["source_path"].endswith("runtime-smoke-results.json")
    assert report["summary"]["result_count"] == 4
    assert report["summary"]["accepted"] is True
    assert report["summary"]["opens_window"] is False
    assert report["summary"]["executes_commands"] is False


def test_runtime_smoke_result_payload_file_accepts_mapping_shape(tmp_path) -> None:
    path = tmp_path / "runtime-smoke-result-map.json"
    path.write_text(
        json.dumps(
            {
                "launch-window": True,
                "navigation-visible": True,
                "no-auto-execution": True,
                "local-only": True,
            }
        ),
        encoding="utf-8",
    )

    report = load_qt_runtime_smoke_result_payload_file(path)

    assert report["result_shape"] == "mapping"
    assert report["summary"]["result_count"] == 4
    assert report["summary"]["failed_count"] == 0
    assert report["summary"]["accepted"] is True


def test_runtime_smoke_result_payload_report_flags_failed_required_result() -> None:
    report = build_qt_runtime_smoke_result_payload_report(
        {"results": [{"check_id": "launch-window", "required": True, "passed": False}]}
    )

    assert report["summary"]["accepted"] is False
    assert report["summary"]["failed_required_count"] == 1
    assert report["summary"]["desktop_problem_count"] == 1


def test_runtime_smoke_result_template_matches_guarded_start_collector() -> None:
    plan = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model(active_page_id="dashboard"))

    template = build_qt_runtime_smoke_result_collector_template(plan)

    assert template["kind"] == "qt_runtime_smoke_result_payload_template"
    assert template["summary"]["result_count"] == plan["start_bundle"]["summary"]["result_placeholder_count"]
    assert template["summary"]["opens_window"] is False
    assert template["results"][0]["passed"] is None


def test_runtime_smoke_result_payload_does_not_import_pyside6(tmp_path) -> None:
    sys.modules.pop("PySide6", None)
    path = tmp_path / "runtime-smoke-results.json"
    path.write_text(json.dumps({"results": _passing_results()}), encoding="utf-8")

    report = load_qt_runtime_smoke_result_payload_file(path)

    assert "PySide6" not in sys.modules
    assert report["capabilities"]["requires_pyside6"] is False
