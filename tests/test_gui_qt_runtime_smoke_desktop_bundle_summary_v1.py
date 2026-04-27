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
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_summary import summarize_qt_runtime_smoke_desktop_rehearsal_bundle


def test_desktop_rehearsal_bundle_composes_full_manual_smoke_contract() -> None:
    bundle = build_qt_runtime_smoke_desktop_rehearsal_bundle(sample_wiring_bundle(), language="de")

    assert bundle["kind"] == "qt_runtime_smoke_desktop_rehearsal_bundle"
    assert bundle["ready_for_manual_desktop_smoke"] is True
    assert bundle["summary"]["manual_step_count"] == 5
    assert bundle["summary"]["hint_count"] == 0
    assert bundle["summary"]["opens_window"] is False
    assert bundle["summary"]["executes_commands"] is False
    assert "Ready: True" in summarize_qt_runtime_smoke_desktop_rehearsal_bundle(bundle)


def test_desktop_rehearsal_bundle_blocks_failed_wiring() -> None:
    bundle = build_qt_runtime_smoke_desktop_rehearsal_bundle(sample_wiring_bundle(ready=False, problems=2))

    assert bundle["ready_for_manual_desktop_smoke"] is False
    assert bundle["summary"]["preflight_failed_required_count"] >= 1
    assert bundle["summary"]["hint_count"] >= 1
    assert bundle["audit"]["valid"] is False
