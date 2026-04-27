from __future__ import annotations

from collections.abc import Mapping

from .gui_qt_runtime_smoke_desktop_result_audit import audit_qt_runtime_smoke_desktop_results
from .gui_qt_runtime_smoke_desktop_result_decision import build_qt_runtime_smoke_desktop_result_decision
from .gui_qt_runtime_smoke_desktop_result_export import build_qt_runtime_smoke_desktop_result_export
from .gui_qt_runtime_smoke_desktop_result_history import build_qt_runtime_smoke_desktop_result_history_entry
from .gui_qt_runtime_smoke_desktop_result_report import build_qt_runtime_smoke_desktop_result_report
from .gui_qt_runtime_smoke_desktop_result_snapshot import build_qt_runtime_smoke_desktop_result_snapshot
from .gui_qt_runtime_smoke_desktop_result_summary import summarize_qt_runtime_smoke_desktop_results
from .gui_qt_runtime_smoke_desktop_result_validator import validate_qt_runtime_smoke_desktop_results

QT_RUNTIME_SMOKE_DESKTOP_RESULT_BUNDLE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_result_bundle(results_payload: Mapping[str, object] | list[Mapping[str, object]]) -> dict[str, object]:
    validation = validate_qt_runtime_smoke_desktop_results(results_payload)
    summary = summarize_qt_runtime_smoke_desktop_results(validation)
    audit = audit_qt_runtime_smoke_desktop_results(validation)
    decision = build_qt_runtime_smoke_desktop_result_decision(summary, audit)
    report = build_qt_runtime_smoke_desktop_result_report(validation, summary, audit, decision)
    export = build_qt_runtime_smoke_desktop_result_export(report)
    history_entry = build_qt_runtime_smoke_desktop_result_history_entry(report)
    snapshot = build_qt_runtime_smoke_desktop_result_snapshot(report)
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_RESULT_BUNDLE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_result_bundle",
        "validation": validation,
        "result_summary": summary,
        "audit": audit,
        "decision": decision,
        "report": report,
        "export": export,
        "history_entry": history_entry,
        "snapshot": snapshot,
        "accepted": report["accepted"],
        "summary": {
            "accepted": report["accepted"],
            "decision": decision["decision"],
            "result_count": summary["result_count"],
            "problem_count": audit["problem_count"],
            "failed_required_count": summary["failed_required_count"],
            "missing_required_count": summary["missing_required_count"],
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


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_RESULT_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_result_bundle"]
