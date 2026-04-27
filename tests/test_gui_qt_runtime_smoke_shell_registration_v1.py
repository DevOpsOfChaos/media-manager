from __future__ import annotations
def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_page_handoff", "ready_for_shell_registration": ready, "route": {"route_id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "guards": {"local_only": True, "opens_window": False, "executes_commands": False, "validation_valid": ready}}, "navigation_item": {"id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "visible": True, "security": {"local_only": True, "opens_window": False, "executes_commands": False}, "badge": {"state": "ready" if ready else "blocked", "problem_count": problems}}, "diagnostics": {"ready": ready, "summary": {"total_problem_count": problems, "ready_for_page_registry": ready, "local_only": True, "opens_window": False, "executes_commands": False}}, "summary": {"ready_for_shell_registration": ready, "page_count": 3, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}}
def sample_navigation_items() -> list[dict[str, object]]:
    return [{"id": "dashboard", "page_id": "dashboard", "label": "Dashboard", "enabled": True}, {"id": "people-review", "page_id": "people-review", "label": "People Review", "enabled": True}]

from media_manager.core.gui_qt_runtime_smoke_shell_registration import build_qt_runtime_smoke_shell_registration
def test_shell_registration_preserves_route_navigation_and_safety() -> None:
    r = build_qt_runtime_smoke_shell_registration(sample_page_handoff())
    assert r["page_id"] == "runtime-smoke"; assert r["enabled"] is True; assert r["summary"]["local_only"] is True; assert r["summary"]["opens_window"] is False; assert r["summary"]["executes_commands"] is False
def test_shell_registration_disabled_when_handoff_not_ready() -> None:
    r = build_qt_runtime_smoke_shell_registration(sample_page_handoff(ready=False, problems=1))
    assert r["enabled"] is False; assert r["summary"]["problem_count"] == 1
