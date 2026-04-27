from __future__ import annotations

def sample_rehearsal_bundle(*, ready: bool = True) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_rehearsal_bundle",
        "ready_for_manual_desktop_smoke": ready,
        "ready": ready,
        "summary": {"ready": ready, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

from media_manager.core.gui_qt_runtime_smoke_desktop_start_bundle import build_qt_runtime_smoke_desktop_start_bundle

def test_all_desktop_start_bundle_parts_remain_headless_and_local() -> None:
    bundle = build_qt_runtime_smoke_desktop_start_bundle(sample_rehearsal_bundle(), language="de")
    parts = [bundle, bundle["start_plan"], bundle["operator_sheet"], bundle["result_collector"], bundle["run_manifest"], bundle["issue_report"], bundle["operator_notes"], bundle["audit"], bundle["snapshot"]]
    for part in parts:
        assert part["capabilities"]["requires_pyside6"] is False
        assert part["capabilities"]["opens_window"] is False
        assert part["capabilities"]["executes_commands"] is False
        assert part["capabilities"]["local_only"] is True
