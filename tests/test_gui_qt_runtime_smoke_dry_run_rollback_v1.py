from __future__ import annotations

def sample_integration_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_integration_bundle", "ready_for_guarded_shell_wiring": ready, "summary": {"ready_for_guarded_shell_wiring": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_shell_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_shell_bundle", "ready_for_shell": ready, "summary": {"ready_for_shell": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "commands": {"commands": [{"id": "runtime-smoke.open", "label": "Open Runtime Smoke page", "enabled": ready, "requires_confirmation": False}, {"id": "runtime-smoke.refresh", "label": "Refresh Runtime Smoke state", "enabled": True, "requires_confirmation": False}, {"id": "runtime-smoke.start-manual-smoke", "label": "Start manual Qt smoke", "enabled": ready, "requires_confirmation": True}]}, "status_slot": {"state": "ready" if ready else "blocked", "text": "Runtime Smoke ready" if ready else "Runtime Smoke needs attention", "problem_count": problems}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_routes() -> list[dict[str, object]]:
    return [{"route_id": "dashboard", "page_id": "dashboard"}, {"route_id": "people-review", "page_id": "people-review"}]

from media_manager.core.gui_qt_runtime_smoke_command_dispatch_plan import build_qt_runtime_smoke_command_dispatch_plan
from media_manager.core.gui_qt_runtime_smoke_page_loader_contract import build_qt_runtime_smoke_page_loader_contract
from media_manager.core.gui_qt_runtime_smoke_router_patch import build_qt_runtime_smoke_router_patch
from media_manager.core.gui_qt_runtime_smoke_shell_wiring_plan import build_qt_runtime_smoke_shell_wiring_plan
from media_manager.core.gui_qt_runtime_smoke_status_footer_patch import build_qt_runtime_smoke_status_footer_patch
from media_manager.core.gui_qt_runtime_smoke_wiring_dry_run import build_qt_runtime_smoke_wiring_dry_run
from media_manager.core.gui_qt_runtime_smoke_wiring_rollback_plan import build_qt_runtime_smoke_wiring_rollback_plan
def test_dry_run_and_rollback_cover_all_wiring_targets() -> None:
    plan=build_qt_runtime_smoke_shell_wiring_plan(sample_integration_bundle(), sample_shell_bundle()); router=build_qt_runtime_smoke_router_patch(plan, existing_routes=sample_routes())
    dry=build_qt_runtime_smoke_wiring_dry_run(router, build_qt_runtime_smoke_page_loader_contract(plan), build_qt_runtime_smoke_command_dispatch_plan(plan), build_qt_runtime_smoke_status_footer_patch(plan)); rollback=build_qt_runtime_smoke_wiring_rollback_plan(plan, router)
    assert dry["summary"]["action_count"] == 4; assert dry["summary"]["ready"] is True; assert dry["summary"]["immediate_execution_count"] == 0; assert rollback["summary"]["operation_count"] == 4; assert rollback["summary"]["manual_only"] is True
