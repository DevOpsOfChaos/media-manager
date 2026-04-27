from __future__ import annotations

def sample_rehearsal_bundle(*, ready: bool = True) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_rehearsal_bundle",
        "ready_for_manual_desktop_smoke": ready,
        "ready": ready,
        "summary": {"ready": ready, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

from media_manager.core.gui_qt_runtime_smoke_desktop_operator_sheet import build_qt_runtime_smoke_desktop_operator_sheet
from media_manager.core.gui_qt_runtime_smoke_desktop_result_collector import apply_qt_runtime_smoke_desktop_results, build_qt_runtime_smoke_desktop_result_collector
from media_manager.core.gui_qt_runtime_smoke_desktop_run_manifest import build_qt_runtime_smoke_desktop_run_manifest
from media_manager.core.gui_qt_runtime_smoke_desktop_start_plan import build_qt_runtime_smoke_desktop_start_plan

def test_result_collector_and_manifest_are_metadata_only() -> None:
    plan = build_qt_runtime_smoke_desktop_start_plan(sample_rehearsal_bundle())
    sheet = build_qt_runtime_smoke_desktop_operator_sheet(plan)
    collector = build_qt_runtime_smoke_desktop_result_collector(sheet)
    manifest = build_qt_runtime_smoke_desktop_run_manifest(plan, sheet, recorded_at_utc="2026-04-27T20:00:00Z")
    assert collector["summary"]["result_count"] == 5
    assert collector["summary"]["completed_result_count"] == 0
    assert manifest["privacy"]["contains_face_crops"] is False
    assert manifest["privacy"]["telemetry_allowed"] is False

def test_apply_results_tracks_failed_required_checks() -> None:
    plan = build_qt_runtime_smoke_desktop_start_plan(sample_rehearsal_bundle())
    sheet = build_qt_runtime_smoke_desktop_operator_sheet(plan)
    collector = build_qt_runtime_smoke_desktop_result_collector(sheet)
    applied = apply_qt_runtime_smoke_desktop_results(collector, {"confirm-no-auto-apply": False})
    assert applied["summary"]["completed_result_count"] == 1
    assert applied["summary"]["failed_required_count"] == 1
