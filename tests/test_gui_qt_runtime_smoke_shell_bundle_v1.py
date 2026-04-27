from __future__ import annotations
def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_page_handoff", "ready_for_shell_registration": ready, "route": {"route_id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "guards": {"local_only": True, "opens_window": False, "executes_commands": False, "validation_valid": ready}}, "navigation_item": {"id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "visible": True, "security": {"local_only": True, "opens_window": False, "executes_commands": False}, "badge": {"state": "ready" if ready else "blocked", "problem_count": problems}}, "diagnostics": {"ready": ready, "summary": {"total_problem_count": problems, "ready_for_page_registry": ready, "local_only": True, "opens_window": False, "executes_commands": False}}, "summary": {"ready_for_shell_registration": ready, "page_count": 3, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}}
def sample_navigation_items() -> list[dict[str, object]]:
    return [{"id": "dashboard", "page_id": "dashboard", "label": "Dashboard", "enabled": True}, {"id": "people-review", "page_id": "people-review", "label": "People Review", "enabled": True}]

from media_manager.core.gui_qt_runtime_smoke_shell_bundle import build_qt_runtime_smoke_shell_bundle
def test_shell_bundle_composes_registration_navigation_commands_and_report() -> None:
    b = build_qt_runtime_smoke_shell_bundle(sample_page_handoff(), existing_navigation_items=sample_navigation_items())
    assert b["kind"] == "qt_runtime_smoke_shell_bundle"; assert b["ready_for_shell"] is True; assert b["summary"]["navigation_item_count"] == 1; assert b["summary"]["command_count"] == 4; assert b["summary"]["toolbar_button_count"] == 3; assert b["summary"]["opens_window"] is False; assert b["summary"]["executes_commands"] is False; assert b["report"]["ready"] is True; assert len(b["snapshot"]["payload_hash"]) == 64
def test_shell_bundle_not_ready_when_handoff_has_problems() -> None:
    b = build_qt_runtime_smoke_shell_bundle(sample_page_handoff(ready=False, problems=1), existing_navigation_items=sample_navigation_items())
    assert b["ready_for_shell"] is False; assert b["summary"]["problem_count"] >= 1; assert b["shell_registration"]["enabled"] is False
