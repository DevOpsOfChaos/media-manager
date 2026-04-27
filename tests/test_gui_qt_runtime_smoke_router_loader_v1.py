from __future__ import annotations

def sample_integration_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_integration_bundle", "ready_for_guarded_shell_wiring": ready, "summary": {"ready_for_guarded_shell_wiring": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_shell_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_shell_bundle", "ready_for_shell": ready, "summary": {"ready_for_shell": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "commands": {"commands": [{"id": "runtime-smoke.open", "label": "Open Runtime Smoke page", "enabled": ready, "requires_confirmation": False}, {"id": "runtime-smoke.refresh", "label": "Refresh Runtime Smoke state", "enabled": True, "requires_confirmation": False}, {"id": "runtime-smoke.start-manual-smoke", "label": "Start manual Qt smoke", "enabled": ready, "requires_confirmation": True}]}, "status_slot": {"state": "ready" if ready else "blocked", "text": "Runtime Smoke ready" if ready else "Runtime Smoke needs attention", "problem_count": problems}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_routes() -> list[dict[str, object]]:
    return [{"route_id": "dashboard", "page_id": "dashboard"}, {"route_id": "people-review", "page_id": "people-review"}]

from media_manager.core.gui_qt_runtime_smoke_page_loader_contract import build_qt_runtime_smoke_page_loader_contract
from media_manager.core.gui_qt_runtime_smoke_router_patch import build_qt_runtime_smoke_router_patch, collect_qt_runtime_smoke_route_ids
from media_manager.core.gui_qt_runtime_smoke_shell_wiring_plan import build_qt_runtime_smoke_shell_wiring_plan
def test_router_patch_and_loader_contract_are_safe_and_lazy() -> None:
    plan=build_qt_runtime_smoke_shell_wiring_plan(sample_integration_bundle(), sample_shell_bundle()); router=build_qt_runtime_smoke_router_patch(plan, existing_routes=sample_routes()); loader=build_qt_runtime_smoke_page_loader_contract(plan)
    assert router["summary"]["runtime_smoke_route_count"] == 1; assert collect_qt_runtime_smoke_route_ids(router) == ["dashboard", "people-review", "runtime-smoke"]; assert loader["lazy_import"] is True; assert loader["contract_requires_pyside6"] is False; assert loader["render_requires_pyside6"] is True; assert loader["summary"]["failed_required_precondition_count"] == 0
def test_loader_contract_blocks_when_wiring_plan_not_ready() -> None:
    plan=build_qt_runtime_smoke_shell_wiring_plan(sample_integration_bundle(ready=False, problems=1), sample_shell_bundle()); loader=build_qt_runtime_smoke_page_loader_contract(plan)
    assert loader["enabled"] is False; assert loader["summary"]["failed_required_precondition_count"] == 1
