from __future__ import annotations


def sample_adapter_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_adapter_bundle",
        "ready_for_qt_runtime": ready,
        "summary": {"problem_count": problems, "local_only": True, "ready_for_qt_runtime": ready},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }


def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_page_handoff",
        "ready_for_shell_registration": ready,
        "summary": {"problem_count": problems, "local_only": True, "ready_for_shell_registration": ready},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }


def sample_shell_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_shell_bundle",
        "ready_for_shell": ready,
        "summary": {"problem_count": problems, "local_only": True, "ready_for_shell": ready},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

from media_manager.core.gui_qt_runtime_smoke_integration_bundle import build_qt_runtime_smoke_integration_bundle
from media_manager.core.gui_qt_runtime_smoke_integration_report import summarize_qt_runtime_smoke_integration_report
from media_manager.core.gui_qt_runtime_smoke_integration_snapshot import build_qt_runtime_smoke_integration_snapshot


def test_integration_report_and_snapshot_are_stable() -> None:
    bundle = build_qt_runtime_smoke_integration_bundle(
        adapter_bundle=sample_adapter_bundle(),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )
    report = bundle["report"]
    snapshot_a = build_qt_runtime_smoke_integration_snapshot(report)
    snapshot_b = build_qt_runtime_smoke_integration_snapshot(report)

    assert report["ready"] is True
    assert "Opens window: False" in summarize_qt_runtime_smoke_integration_report(report)
    assert snapshot_a["payload_hash"] == snapshot_b["payload_hash"]
    assert len(snapshot_a["payload_hash"]) == 64
    assert snapshot_a["summary"]["local_only"] is True
