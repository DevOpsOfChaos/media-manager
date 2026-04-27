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

from media_manager.core.gui_qt_runtime_smoke_desktop_manual_steps import build_qt_runtime_smoke_desktop_manual_steps
from media_manager.core.gui_qt_runtime_smoke_desktop_preflight import build_qt_runtime_smoke_desktop_preflight
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_plan import build_qt_runtime_smoke_desktop_rehearsal_plan
from media_manager.core.gui_qt_runtime_smoke_desktop_session_plan import build_qt_runtime_smoke_desktop_session_plan


def test_desktop_session_plan_and_german_steps_are_manual_only() -> None:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(sample_wiring_bundle(), language="de")
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)
    session = build_qt_runtime_smoke_desktop_session_plan(plan, preflight)
    steps = build_qt_runtime_smoke_desktop_manual_steps(session, language="de")

    assert session["ready"] is True
    assert "--active-page runtime-smoke" in session["display_command"]
    assert session["summary"]["manual_phase_count"] == 5
    assert steps["language"] == "de"
    assert steps["summary"]["manual_step_count"] == 5
    assert any("App manuell starten" == step["label"] for step in steps["steps"])
