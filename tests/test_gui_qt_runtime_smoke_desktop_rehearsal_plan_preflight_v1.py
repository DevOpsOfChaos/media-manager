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

from media_manager.core.gui_qt_runtime_smoke_desktop_preflight import build_qt_runtime_smoke_desktop_preflight
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_plan import build_qt_runtime_smoke_desktop_rehearsal_plan


def test_desktop_rehearsal_plan_and_preflight_are_ready_for_clean_wiring() -> None:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(sample_wiring_bundle(), language="de")
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)

    assert plan["ready"] is True
    assert plan["language"] == "de"
    assert plan["summary"]["step_count"] == 5
    assert plan["launch"]["executes_immediately"] is False
    assert preflight["summary"]["ready"] is True
    assert preflight["summary"]["failed_required_count"] == 0


def test_desktop_preflight_blocks_not_ready_wiring() -> None:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(sample_wiring_bundle(ready=False, problems=2))
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)

    assert plan["ready"] is False
    assert plan["summary"]["wiring_problem_count"] == 2
    assert preflight["summary"]["ready"] is False
    assert preflight["summary"]["failed_required_count"] >= 1
