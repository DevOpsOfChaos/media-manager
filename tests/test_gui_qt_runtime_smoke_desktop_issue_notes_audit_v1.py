from __future__ import annotations

def sample_rehearsal_bundle(*, ready: bool = True) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_rehearsal_bundle",
        "ready_for_manual_desktop_smoke": ready,
        "ready": ready,
        "summary": {"ready": ready, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

from media_manager.core.gui_qt_runtime_smoke_desktop_issue_report import build_qt_runtime_smoke_desktop_issue_report
from media_manager.core.gui_qt_runtime_smoke_desktop_operator_notes import build_qt_runtime_smoke_desktop_operator_notes
from media_manager.core.gui_qt_runtime_smoke_desktop_operator_sheet import build_qt_runtime_smoke_desktop_operator_sheet
from media_manager.core.gui_qt_runtime_smoke_desktop_result_collector import apply_qt_runtime_smoke_desktop_results, build_qt_runtime_smoke_desktop_result_collector
from media_manager.core.gui_qt_runtime_smoke_desktop_run_manifest import build_qt_runtime_smoke_desktop_run_manifest
from media_manager.core.gui_qt_runtime_smoke_desktop_start_audit import audit_qt_runtime_smoke_desktop_start
from media_manager.core.gui_qt_runtime_smoke_desktop_start_plan import build_qt_runtime_smoke_desktop_start_plan

def test_issue_report_notes_and_audit_accept_clean_placeholders() -> None:
    plan = build_qt_runtime_smoke_desktop_start_plan(sample_rehearsal_bundle())
    sheet = build_qt_runtime_smoke_desktop_operator_sheet(plan)
    collector = build_qt_runtime_smoke_desktop_result_collector(sheet)
    issues = build_qt_runtime_smoke_desktop_issue_report(collector)
    notes = build_qt_runtime_smoke_desktop_operator_notes(language="de")
    audit = audit_qt_runtime_smoke_desktop_start(plan, build_qt_runtime_smoke_desktop_run_manifest(plan, sheet), issues)
    assert issues["summary"]["issue_count"] == 0
    assert notes["language"] == "de"
    assert audit["valid"] is True
    assert audit["summary"]["executes_commands"] is False

def test_issue_report_and_audit_block_failed_required_result() -> None:
    plan = build_qt_runtime_smoke_desktop_start_plan(sample_rehearsal_bundle())
    sheet = build_qt_runtime_smoke_desktop_operator_sheet(plan)
    collector = build_qt_runtime_smoke_desktop_result_collector(sheet)
    failed = apply_qt_runtime_smoke_desktop_results(collector, {"confirm-no-auto-apply": False})
    issues = build_qt_runtime_smoke_desktop_issue_report(failed)
    audit = audit_qt_runtime_smoke_desktop_start(plan, build_qt_runtime_smoke_desktop_run_manifest(plan, sheet), issues)
    assert issues["summary"]["has_blocking_issues"] is True
    assert audit["valid"] is False
    assert audit["problems"][0]["code"] == "desktop_smoke_has_blocking_issues"
