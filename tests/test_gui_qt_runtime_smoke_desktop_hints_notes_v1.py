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

from media_manager.core.gui_qt_runtime_smoke_desktop_failure_hints import build_qt_runtime_smoke_desktop_failure_hints
from media_manager.core.gui_qt_runtime_smoke_desktop_launch_notes import build_qt_runtime_smoke_desktop_launch_notes
from media_manager.core.gui_qt_runtime_smoke_desktop_manual_steps import build_qt_runtime_smoke_desktop_manual_steps
from media_manager.core.gui_qt_runtime_smoke_desktop_preflight import build_qt_runtime_smoke_desktop_preflight
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_plan import build_qt_runtime_smoke_desktop_rehearsal_plan
from media_manager.core.gui_qt_runtime_smoke_desktop_session_plan import build_qt_runtime_smoke_desktop_session_plan


def test_failure_hints_empty_for_clean_preflight_and_launch_notes_are_manual() -> None:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(sample_wiring_bundle())
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)
    session = build_qt_runtime_smoke_desktop_session_plan(plan, preflight)
    steps = build_qt_runtime_smoke_desktop_manual_steps(session)
    hints = build_qt_runtime_smoke_desktop_failure_hints(preflight)
    notes = build_qt_runtime_smoke_desktop_launch_notes(session, steps)

    assert hints["summary"]["hint_count"] == 0
    assert notes["ready"] is True
    assert notes["summary"]["opens_window"] is False
    assert notes["summary"]["executes_commands"] is False
    assert 'python -m pip install -e ".[gui]"' == notes["install_hint"]


def test_failure_hints_explain_blocked_preflight() -> None:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(sample_wiring_bundle(ready=False, problems=1))
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)
    hints = build_qt_runtime_smoke_desktop_failure_hints(preflight)

    assert hints["summary"]["has_blockers"] is True
    assert hints["summary"]["blocking_hint_count"] >= 1
