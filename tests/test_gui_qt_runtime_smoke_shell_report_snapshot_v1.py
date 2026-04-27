from __future__ import annotations
def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {"kind": "qt_runtime_smoke_page_handoff", "ready_for_shell_registration": ready, "route": {"route_id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "guards": {"local_only": True, "opens_window": False, "executes_commands": False, "validation_valid": ready}}, "navigation_item": {"id": "runtime-smoke", "page_id": "runtime-smoke", "label": "Runtime Smoke", "enabled": ready, "visible": True, "security": {"local_only": True, "opens_window": False, "executes_commands": False}, "badge": {"state": "ready" if ready else "blocked", "problem_count": problems}}, "diagnostics": {"ready": ready, "summary": {"total_problem_count": problems, "ready_for_page_registry": ready, "local_only": True, "opens_window": False, "executes_commands": False}}, "summary": {"ready_for_shell_registration": ready, "page_count": 3, "problem_count": problems, "local_only": True, "opens_window": False, "executes_commands": False}}
def sample_navigation_items() -> list[dict[str, object]]:
    return [{"id": "dashboard", "page_id": "dashboard", "label": "Dashboard", "enabled": True}, {"id": "people-review", "page_id": "people-review", "label": "People Review", "enabled": True}]

from media_manager.core.gui_qt_runtime_smoke_shell_bundle import build_qt_runtime_smoke_shell_bundle
from media_manager.core.gui_qt_runtime_smoke_shell_report import build_qt_runtime_smoke_shell_report, summarize_qt_runtime_smoke_shell_report
from media_manager.core.gui_qt_runtime_smoke_shell_snapshot import build_qt_runtime_smoke_shell_snapshot
def test_shell_report_and_snapshot_are_stable_and_safe() -> None:
    b = build_qt_runtime_smoke_shell_bundle(sample_page_handoff(), existing_navigation_items=sample_navigation_items()); report = build_qt_runtime_smoke_shell_report(b); a = build_qt_runtime_smoke_shell_snapshot(b); z = build_qt_runtime_smoke_shell_snapshot(b)
    assert report["ready"] is True; assert "Opens window: False" in summarize_qt_runtime_smoke_shell_report(report); assert a["payload_hash"] == z["payload_hash"]; assert len(a["payload_hash"]) == 64; assert a["summary"]["local_only"] is True
