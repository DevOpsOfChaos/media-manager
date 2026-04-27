from __future__ import annotations
def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_page_handoff", "ready_for_shell_registration": ready, "route": {"route_id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "guards": {"local_only": True, "opens_window": False, "executes_commands": False, "validation_valid": ready}}, "navigation_item": {"id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "visible": True, "security": {"local_only": True, "opens_window": False, "executes_commands": False}, "badge": {"state": "ready" if ready else "blocked", "problem_count": problems}}, "diagnostics": {"ready": ready, "summary": {"total_problem_count": problems, "ready_for_page_registry": ready, "local_only": True, "opens_window": False, "executes_commands": False}}, "summary": {"ready_for_shell_registration": ready, "page_count": 3, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}}
def sample_navigation_items() -> list[dict[str, object]]:
    return [{"id": "dashboard", "page_id": "dashboard", "label": "Dashboard", "enabled": True}, {"id": "people-review", "page_id": "people-review", "label": "People Review", "enabled": True}]

from media_manager.core.gui_qt_runtime_smoke_shell_commands import build_qt_runtime_smoke_shell_commands
from media_manager.core.gui_qt_runtime_smoke_shell_registration import build_qt_runtime_smoke_shell_registration
from media_manager.core.gui_qt_runtime_smoke_shell_toolbar import build_qt_runtime_smoke_shell_toolbar
def test_shell_commands_and_toolbar_are_deferred_or_confirmed() -> None:
    commands = build_qt_runtime_smoke_shell_commands(build_qt_runtime_smoke_shell_registration(sample_page_handoff())); toolbar = build_qt_runtime_smoke_shell_toolbar(commands)
    assert commands["summary"]["command_count"] == 4; assert commands["summary"]["confirmation_command_count"] == 1; assert commands["summary"]["immediate_execution_count"] == 0; assert toolbar["summary"]["button_count"] == 3; assert toolbar["summary"]["confirmation_button_count"] == 1
def test_shell_commands_disable_launch_when_registration_disabled() -> None:
    commands = build_qt_runtime_smoke_shell_commands(build_qt_runtime_smoke_shell_registration(sample_page_handoff(ready=False, problems=1)))
    start = [c for c in commands["commands"] if c["id"] == "runtime-smoke.start-manual-smoke"][0]
    assert start["enabled"] is False; assert start["requires_confirmation"] is True
