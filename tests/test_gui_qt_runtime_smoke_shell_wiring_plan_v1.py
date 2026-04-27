from __future__ import annotations

def sample_integration_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_integration_bundle", "ready_for_guarded_shell_wiring": ready, "summary": {"ready_for_guarded_shell_wiring": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_shell_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_shell_bundle", "ready_for_shell": ready, "summary": {"ready_for_shell": ready, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}, "commands": {"commands": [{"id": "runtime-smoke.open", "label": "Open Runtime Smoke page", "enabled": ready, "requires_confirmation": False}, {"id": "runtime-smoke.refresh", "label": "Refresh Runtime Smoke state", "enabled": True, "requires_confirmation": False}, {"id": "runtime-smoke.start-manual-smoke", "label": "Start manual Qt smoke", "enabled": ready, "requires_confirmation": True}]}, "status_slot": {"state": "ready" if ready else "blocked", "text": "Runtime Smoke ready" if ready else "Runtime Smoke needs attention", "problem_count": problems}, "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True}}

def sample_routes() -> list[dict[str, object]]:
    return [{"route_id": "dashboard", "page_id": "dashboard"}, {"route_id": "people-review", "page_id": "people-review"}]

from media_manager.core.gui_qt_runtime_smoke_shell_wiring_plan import build_qt_runtime_smoke_shell_wiring_plan
def test_shell_wiring_plan_combines_integration_and_shell_readiness() -> None:
    plan=build_qt_runtime_smoke_shell_wiring_plan(sample_integration_bundle(), sample_shell_bundle())
    assert plan["ready"] is True; assert plan["summary"]["step_count"] == 5; assert plan["summary"]["ready_step_count"] == 5; assert plan["summary"]["opens_window"] is False; assert plan["summary"]["executes_commands"] is False
def test_shell_wiring_plan_not_ready_when_shell_blocked() -> None:
    plan=build_qt_runtime_smoke_shell_wiring_plan(sample_integration_bundle(), sample_shell_bundle(ready=False, problems=1))
    assert plan["ready"] is False; assert plan["summary"]["problem_count"] == 1
