from __future__ import annotations

def sample_integration_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_integration_bundle", "ready_for_guarded_shell_wiring": ready, "summary": {"ready_for_guarded_shell_wiring": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_shell_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_shell_bundle", "ready_for_shell": ready, "summary": {"ready_for_shell": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "commands": {"commands": [{"id": "runtime-smoke.open", "label": "Open Runtime Smoke page", "enabled": ready, "requires_confirmation": False}, {"id": "runtime-smoke.refresh", "label": "Refresh Runtime Smoke state", "enabled": True, "requires_confirmation": False}, {"id": "runtime-smoke.start-manual-smoke", "label": "Start manual Qt smoke", "enabled": ready, "requires_confirmation": True}]}, "status_slot": {"state": "ready" if ready else "blocked", "text": "Runtime Smoke ready" if ready else "Runtime Smoke needs attention", "problem_count": problems}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_routes() -> list[dict[str, object]]:
    return [{"route_id": "dashboard", "page_id": "dashboard"}, {"route_id": "people-review", "page_id": "people-review"}]

from media_manager.core.gui_qt_runtime_smoke_wiring_bundle import build_qt_runtime_smoke_wiring_bundle
def test_wiring_bundle_not_ready_when_integration_bundle_blocked() -> None:
    bundle=build_qt_runtime_smoke_wiring_bundle(sample_integration_bundle(ready=False, problems=2), sample_shell_bundle(), existing_routes=sample_routes())
    assert bundle["ready_for_guarded_shell_wiring"] is False; assert bundle["summary"]["problem_count"] > 0; assert bundle["page_loader_contract"]["enabled"] is False; assert bundle["dry_run"]["summary"]["ready"] is False
