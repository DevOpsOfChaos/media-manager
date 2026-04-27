from __future__ import annotations

def sample_rehearsal_bundle(*, ready: bool = True) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_rehearsal_bundle",
        "ready_for_manual_desktop_smoke": ready,
        "ready": ready,
        "summary": {"ready": ready, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

from media_manager.core.gui_qt_runtime_smoke_desktop_operator_sheet import build_qt_runtime_smoke_desktop_operator_sheet
from media_manager.core.gui_qt_runtime_smoke_desktop_start_plan import build_qt_runtime_smoke_desktop_start_plan

def test_start_plan_and_operator_sheet_are_ready_for_green_rehearsal() -> None:
    plan = build_qt_runtime_smoke_desktop_start_plan(sample_rehearsal_bundle(), language="de")
    sheet = build_qt_runtime_smoke_desktop_operator_sheet(plan)
    assert plan["ready_for_manual_start"] is True
    assert plan["summary"]["failed_required_count"] == 0
    assert sheet["ready"] is True
    assert sheet["summary"]["check_count"] == 5
    assert any("Keine Apply" in check["label"] for check in sheet["checks"])

def test_start_plan_blocks_failed_rehearsal() -> None:
    plan = build_qt_runtime_smoke_desktop_start_plan(sample_rehearsal_bundle(ready=False))
    assert plan["ready_for_manual_start"] is False
    assert plan["summary"]["failed_required_count"] == 1
