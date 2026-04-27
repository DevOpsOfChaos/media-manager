from __future__ import annotations

def sample_integration_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_integration_bundle", "ready_for_guarded_shell_wiring": ready, "summary": {"ready_for_guarded_shell_wiring": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_shell_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_shell_bundle", "ready_for_shell": ready, "summary": {"ready_for_shell": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "commands": {"commands": [{"id": "runtime-smoke.open", "label": "Open Runtime Smoke page", "enabled": ready, "requires_confirmation": False}, {"id": "runtime-smoke.refresh", "label": "Refresh Runtime Smoke state", "enabled": True, "requires_confirmation": False}, {"id": "runtime-smoke.start-manual-smoke", "label": "Start manual Qt smoke", "enabled": ready, "requires_confirmation": True}]}, "status_slot": {"state": "ready" if ready else "blocked", "text": "Runtime Smoke ready" if ready else "Runtime Smoke needs attention", "problem_count": problems}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_routes() -> list[dict[str, object]]:
    return [{"route_id": "dashboard", "page_id": "dashboard"}, {"route_id": "people-review", "page_id": "people-review"}]

from media_manager.core.gui_qt_runtime_smoke_wiring_bundle import build_qt_runtime_smoke_wiring_bundle
from media_manager.core.gui_qt_runtime_smoke_wiring_snapshot import build_qt_runtime_smoke_wiring_snapshot
from media_manager.core.gui_qt_runtime_smoke_wiring_summary import summarize_qt_runtime_smoke_wiring_bundle
def test_wiring_bundle_composes_all_guarded_shell_wiring_parts() -> None:
    bundle=build_qt_runtime_smoke_wiring_bundle(sample_integration_bundle(), sample_shell_bundle(), existing_routes=sample_routes())
    assert bundle["kind"] == "qt_runtime_smoke_wiring_bundle"; assert bundle["ready_for_guarded_shell_wiring"] is True; assert bundle["summary"]["route_count"] == 1; assert bundle["summary"]["dispatch_count"] == 3; assert bundle["summary"]["rollback_operation_count"] == 4; assert bundle["summary"]["opens_window"] is False; assert bundle["summary"]["executes_commands"] is False; assert "Ready: True" in summarize_qt_runtime_smoke_wiring_bundle(bundle)
def test_wiring_snapshot_is_stable_metadata_only() -> None:
    bundle=build_qt_runtime_smoke_wiring_bundle(sample_integration_bundle(), sample_shell_bundle(), existing_routes=sample_routes()); a=build_qt_runtime_smoke_wiring_snapshot(bundle); b=build_qt_runtime_smoke_wiring_snapshot(bundle)
    assert a["payload_hash"] == b["payload_hash"]; assert len(a["payload_hash"]) == 64; assert a["summary"]["local_only"] is True
