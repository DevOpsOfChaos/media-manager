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

from media_manager.core.gui_qt_runtime_smoke_desktop_launch_notes import build_qt_runtime_smoke_desktop_launch_notes
from media_manager.core.gui_qt_runtime_smoke_desktop_manual_steps import build_qt_runtime_smoke_desktop_manual_steps
from media_manager.core.gui_qt_runtime_smoke_desktop_preflight import build_qt_runtime_smoke_desktop_preflight
from media_manager.core.gui_qt_runtime_smoke_desktop_readiness_badge import build_qt_runtime_smoke_desktop_readiness_badge
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_audit import audit_qt_runtime_smoke_desktop_rehearsal
from media_manager.core.gui_qt_runtime_smoke_desktop_rehearsal_plan import build_qt_runtime_smoke_desktop_rehearsal_plan
from media_manager.core.gui_qt_runtime_smoke_desktop_session_plan import build_qt_runtime_smoke_desktop_session_plan


def test_desktop_rehearsal_audit_and_badge_accept_clean_contract() -> None:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(sample_wiring_bundle())
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)
    session = build_qt_runtime_smoke_desktop_session_plan(plan, preflight)
    steps = build_qt_runtime_smoke_desktop_manual_steps(session)
    notes = build_qt_runtime_smoke_desktop_launch_notes(session, steps)
    audit = audit_qt_runtime_smoke_desktop_rehearsal(plan, preflight, session, notes)
    badge = build_qt_runtime_smoke_desktop_readiness_badge(audit)

    assert audit["valid"] is True
    assert audit["problem_count"] == 0
    assert badge["state"] == "ready"
    assert badge["ready"] is True


def test_desktop_rehearsal_audit_blocks_not_ready_plan() -> None:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(sample_wiring_bundle(ready=False, problems=1))
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)
    session = build_qt_runtime_smoke_desktop_session_plan(plan, preflight)
    steps = build_qt_runtime_smoke_desktop_manual_steps(session)
    notes = build_qt_runtime_smoke_desktop_launch_notes(session, steps)
    audit = audit_qt_runtime_smoke_desktop_rehearsal(plan, preflight, session, notes)
    badge = build_qt_runtime_smoke_desktop_readiness_badge(audit)

    assert audit["valid"] is False
    assert badge["ready"] is False
    assert badge["state"] == "blocked"
