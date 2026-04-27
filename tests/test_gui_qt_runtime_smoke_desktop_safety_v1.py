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


def test_desktop_rehearsal_bundle_never_opens_window_or_executes_commands() -> None:
    bundle = build_qt_runtime_smoke_desktop_rehearsal_bundle(sample_wiring_bundle())

    assert bundle["capabilities"]["opens_window"] is False
    assert bundle["capabilities"]["executes_commands"] is False
    assert bundle["rehearsal_plan"]["launch"]["executes_immediately"] is False
    assert bundle["rehearsal_plan"]["launch"]["opens_window_during_plan"] is False
    assert bundle["preflight"]["summary"]["opens_window"] is False
    assert bundle["session_plan"]["summary"]["executes_commands"] is False
    assert bundle["launch_notes"]["summary"]["local_only"] is True
