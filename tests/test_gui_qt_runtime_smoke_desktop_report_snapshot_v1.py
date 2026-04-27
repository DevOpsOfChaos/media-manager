from __future__ import annotations


def sample_wiring_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_wiring_bundle",
        "ready_for_guarded_shell_wiring": ready,
        "summary": {
            "ready_for_guarded_shell_wiring": ready,
            "problem_count": problems,
            "route_count": 1,
            "dispatch_count": 3,
            "rollback_operation_count": 4,
            "local_only": True,
            "opens_window": False,
            "executes_commands": False,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }

from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_bundle import build_qt_runtime_smoke_desktop_rehearsal_bundle
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_report import summarize_qt_runtime_smoke_desktop_rehearsal_report
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_snapshot import build_qt_runtime_smoke_desktop_rehearsal_snapshot


def test_desktop_report_and_snapshot_are_stable() -> None:
    bundle = build_qt_runtime_smoke_desktop_rehearsal_bundle(sample_wiring_bundle())
    report = bundle["report"]
    snapshot_a = build_qt_runtime_smoke_desktop_rehearsal_snapshot(report)
    snapshot_b = build_qt_runtime_smoke_desktop_rehearsal_snapshot(report)

    assert report["ready"] is True
    assert "Executes commands: False" in summarize_qt_runtime_smoke_desktop_rehearsal_report(report)
    assert snapshot_a["payload_hash"] == snapshot_b["payload_hash"]
    assert len(snapshot_a["payload_hash"]) == 64
    assert snapshot_a["summary"]["local_only"] is True
