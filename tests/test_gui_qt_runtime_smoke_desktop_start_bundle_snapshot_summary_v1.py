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
from media_manager.core.gui_qt_runtime_smoke_desktop_start_snapshot import build_qt_runtime_smoke_desktop_start_snapshot
from media_manager.core.gui_qt_runtime_smoke_desktop_start_summary import summarize_qt_runtime_smoke_desktop_start_bundle

def test_desktop_start_bundle_composes_handoff_parts() -> None:
    bundle = build_qt_runtime_smoke_desktop_start_bundle(sample_rehearsal_bundle(), language="de")
    assert bundle["kind"] == "qt_runtime_smoke_desktop_start_bundle"
    assert bundle["ready_for_manual_desktop_start"] is True
    assert bundle["summary"]["operator_check_count"] == 5
    assert bundle["summary"]["result_placeholder_count"] == 5
    assert bundle["summary"]["opens_window"] is False
    assert bundle["summary"]["executes_commands"] is False
    assert "Ready: True" in summarize_qt_runtime_smoke_desktop_start_bundle(bundle)

def test_desktop_start_snapshot_is_stable() -> None:
    bundle = build_qt_runtime_smoke_desktop_start_bundle(sample_rehearsal_bundle(), language="de")
    snapshot_a = build_qt_runtime_smoke_desktop_start_snapshot(bundle)
    snapshot_b = build_qt_runtime_smoke_desktop_start_snapshot(bundle)
    assert snapshot_a["payload_hash"] == snapshot_b["payload_hash"]
    assert len(snapshot_a["payload_hash"]) == 64
    assert snapshot_a["summary"]["local_only"] is True

def test_desktop_start_bundle_blocks_failed_rehearsal() -> None:
    bundle = build_qt_runtime_smoke_desktop_start_bundle(sample_rehearsal_bundle(ready=False), language="de")
    assert bundle["ready_for_manual_desktop_start"] is False
    assert bundle["summary"]["problem_count"] > 0
