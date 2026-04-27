from __future__ import annotations
from collections.abc import Mapping

from .gui_qt_runtime_smoke_desktop_issue_report import build_qt_runtime_smoke_desktop_issue_report
from .gui_qt_runtime_smoke_desktop_operator_notes import build_qt_runtime_smoke_desktop_operator_notes
from .gui_qt_runtime_smoke_desktop_operator_sheet import build_qt_runtime_smoke_desktop_operator_sheet
from .gui_qt_runtime_smoke_desktop_result_collector import build_qt_runtime_smoke_desktop_result_collector
from .gui_qt_runtime_smoke_desktop_run_manifest import build_qt_runtime_smoke_desktop_run_manifest
from .gui_qt_runtime_smoke_desktop_start_audit import audit_qt_runtime_smoke_desktop_start
from .gui_qt_runtime_smoke_desktop_start_plan import build_qt_runtime_smoke_desktop_start_plan
from .gui_qt_runtime_smoke_desktop_start_snapshot import build_qt_runtime_smoke_desktop_start_snapshot

QT_RUNTIME_SMOKE_DESKTOP_START_BUNDLE_SCHEMA_VERSION = "1.0"

def build_qt_runtime_smoke_desktop_start_bundle(rehearsal_bundle: Mapping[str, object], *, language: str = "de") -> dict[str, object]:
    start_plan = build_qt_runtime_smoke_desktop_start_plan(rehearsal_bundle, language=language)
    sheet = build_qt_runtime_smoke_desktop_operator_sheet(start_plan)
    collector = build_qt_runtime_smoke_desktop_result_collector(sheet)
    manifest = build_qt_runtime_smoke_desktop_run_manifest(start_plan, sheet)
    issues = build_qt_runtime_smoke_desktop_issue_report(collector)
    notes = build_qt_runtime_smoke_desktop_operator_notes(language=language)
    audit = audit_qt_runtime_smoke_desktop_start(start_plan, manifest, issues)
    ready = bool(start_plan.get("ready_for_manual_start")) and bool(audit.get("valid"))
    bundle: dict[str, object] = {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_START_BUNDLE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_start_bundle",
        "start_plan": start_plan,
        "operator_sheet": sheet,
        "result_collector": collector,
        "run_manifest": manifest,
        "issue_report": issues,
        "operator_notes": notes,
        "audit": audit,
        "ready_for_manual_desktop_start": ready,
        "summary": {"ready_for_manual_desktop_start": ready, "operator_check_count": sheet["summary"]["check_count"], "result_placeholder_count": collector["summary"]["result_count"], "issue_count": issues["summary"]["issue_count"], "problem_count": audit["problem_count"], "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }
    bundle["snapshot"] = build_qt_runtime_smoke_desktop_start_snapshot(bundle)
    return bundle

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_START_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_start_bundle"]
