from __future__ import annotations
def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_page_handoff", "ready_for_shell_registration": ready, "route": {"route_id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "guards": {"local_only": True, "opens_window": False, "executes_commands": False, "validation_valid": ready}}, "navigation_item": {"id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "visible": True, "security": {"local_only": True, "opens_window": False, "executes_commands": False}, "badge": {"state": "ready" if ready else "blocked", "problem_count": problems}}, "diagnostics": {"ready": ready, "summary": {"total_problem_count": problems, "ready_for_page_registry": ready, "local_only": True, "opens_window": False, "executes_commands": False}}, "summary": {"ready_for_shell_registration": ready, "page_count": 3, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}}
def sample_navigation_items() -> list[dict[str, object]]:
    return [{"id": "dashboard", "page_id": "dashboard", "label": "Dashboard", "enabled": True}, {"id": "people-review", "page_id": "people-review", "label": "People Review", "enabled": True}]

from media_manager.core.gui_qt_runtime_smoke_shell_bundle import build_qt_runtime_smoke_shell_bundle
from media_manager.core.gui_qt_runtime_smoke_shell_readiness import evaluate_qt_runtime_smoke_shell_readiness
def test_shell_readiness_accepts_complete_safe_bundle_parts() -> None:
    b = build_qt_runtime_smoke_shell_bundle(sample_page_handoff(), existing_navigation_items=sample_navigation_items())
    readiness = evaluate_qt_runtime_smoke_shell_readiness(b["shell_registration"], b["navigation_patch"], b["commands"], b["toolbar"], b["guard"])
    assert readiness["ready"] is True; assert readiness["problem_count"] == 0; assert readiness["summary"]["navigation_item_count"] == 1; assert readiness["summary"]["executes_commands"] is False
def test_shell_readiness_rejects_blocked_registration() -> None:
    b = build_qt_runtime_smoke_shell_bundle(sample_page_handoff(ready=False, problems=1), existing_navigation_items=sample_navigation_items())
    assert b["readiness"]["ready"] is False; codes = {p["code"] for p in b["readiness"]["problems"]}; assert "registration_not_enabled" in codes; assert "guard_blocks_route" in codes
