from __future__ import annotations

from collections.abc import Mapping

from .gui_qt_runtime_smoke_desktop_failure_hints import build_qt_runtime_smoke_desktop_failure_hints
from .gui_qt_runtime_smoke_desktop_launch_notes import build_qt_runtime_smoke_desktop_launch_notes
from .gui_qt_runtime_smoke_desktop_manual_steps import build_qt_runtime_smoke_desktop_manual_steps
from .gui_qt_runtime_smoke_desktop_preflight import build_qt_runtime_smoke_desktop_preflight
from .gui_qt_runtime_smoke_desktop_readiness_badge import build_qt_runtime_smoke_desktop_readiness_badge
from .gui_qt_runtime_smoke_desktop_rehearsal_audit import audit_qt_runtime_smoke_desktop_rehearsal
from .gui_qt_runtime_smoke_desktop_rehearsal_plan import build_qt_runtime_smoke_desktop_rehearsal_plan
from .gui_qt_runtime_smoke_desktop_rehearsal_report import build_qt_runtime_smoke_desktop_rehearsal_report
from .gui_qt_runtime_smoke_desktop_rehearsal_snapshot import build_qt_runtime_smoke_desktop_rehearsal_snapshot
from .gui_qt_runtime_smoke_desktop_session_plan import build_qt_runtime_smoke_desktop_session_plan

QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_BUNDLE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_rehearsal_bundle(
    wiring_bundle: Mapping[str, object],
    *,
    language: str = "en",
    theme: str = "modern-dark",
) -> dict[str, object]:
    plan = build_qt_runtime_smoke_desktop_rehearsal_plan(wiring_bundle, language=language, theme=theme)
    preflight = build_qt_runtime_smoke_desktop_preflight(plan)
    session = build_qt_runtime_smoke_desktop_session_plan(plan, preflight)
    steps = build_qt_runtime_smoke_desktop_manual_steps(session, language=language)
    hints = build_qt_runtime_smoke_desktop_failure_hints(preflight)
    notes = build_qt_runtime_smoke_desktop_launch_notes(session, steps)
    audit = audit_qt_runtime_smoke_desktop_rehearsal(plan, preflight, session, notes)
    badge = build_qt_runtime_smoke_desktop_readiness_badge(audit)
    report = build_qt_runtime_smoke_desktop_rehearsal_report(plan, preflight, session, steps, hints, notes, audit, badge)
    snapshot = build_qt_runtime_smoke_desktop_rehearsal_snapshot(report)
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_BUNDLE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_rehearsal_bundle",
        "rehearsal_plan": plan,
        "preflight": preflight,
        "session_plan": session,
        "manual_steps": steps,
        "failure_hints": hints,
        "launch_notes": notes,
        "audit": audit,
        "readiness_badge": badge,
        "report": report,
        "snapshot": snapshot,
        "ready_for_manual_desktop_smoke": bool(report.get("ready")),
        "summary": {
            "ready_for_manual_desktop_smoke": bool(report.get("ready")),
            "preflight_failed_required_count": report["summary"]["preflight_failed_required_count"],
            "manual_step_count": report["summary"]["manual_step_count"],
            "hint_count": report["summary"]["hint_count"],
            "audit_problem_count": report["summary"]["audit_problem_count"],
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_REHEARSAL_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_rehearsal_bundle"]
