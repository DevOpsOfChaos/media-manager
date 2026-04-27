from __future__ import annotations
def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_page_handoff", "ready_for_shell_registration": ready, "route": {"route_id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "guards": {"local_only": True, "opens_window": False, "executes_commands": False, "validation_valid": ready}}, "navigation_item": {"id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "visible": True, "security": {"local_only": True, "opens_window": False, "executes_commands": False}, "badge": {"state": "ready" if ready else "blocked", "problem_count": problems}}, "diagnostics": {"ready": ready, "summary": {"total_problem_count": problems, "ready_for_page_registry": ready, "local_only": True, "opens_window": False, "executes_commands": False}}, "summary": {"ready_for_shell_registration": ready, "page_count": 3, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}}
def sample_navigation_items() -> list[dict[str, object]]:
    return [{"id": "dashboard", "page_id": "dashboard", "label": "Dashboard", "enabled": True}, {"id": "people-review", "page_id": "people-review", "label": "People Review", "enabled": True}]

from media_manager.core.gui_qt_runtime_smoke_shell_navigation_patch import build_qt_runtime_smoke_shell_navigation_patch, collect_qt_runtime_smoke_navigation_ids
from media_manager.core.gui_qt_runtime_smoke_shell_registration import build_qt_runtime_smoke_shell_registration
def test_navigation_patch_adds_runtime_smoke_item() -> None:
    patch = build_qt_runtime_smoke_shell_navigation_patch(build_qt_runtime_smoke_shell_registration(sample_page_handoff()), existing_items=sample_navigation_items())
    assert patch["summary"]["after_count"] == 3; assert patch["summary"]["runtime_smoke_item_count"] == 1; assert collect_qt_runtime_smoke_navigation_ids(patch) == ["dashboard", "people-review", "runtime-smoke"]
def test_navigation_patch_replaces_existing_runtime_smoke_item() -> None:
    existing = [*sample_navigation_items(), {"id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Old"}]
    patch = build_qt_runtime_smoke_shell_navigation_patch(build_qt_runtime_smoke_shell_registration(sample_page_handoff()), existing_items=existing)
    assert patch["summary"]["after_count"] == 3; assert patch["summary"]["replaced_existing"] is True
