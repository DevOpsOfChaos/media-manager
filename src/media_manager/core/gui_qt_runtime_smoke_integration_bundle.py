from __future__ import annotations

from collections.abc import Mapping

from .gui_qt_runtime_smoke_integration_checklist import build_qt_runtime_smoke_integration_checklist
from .gui_qt_runtime_smoke_integration_gate import evaluate_qt_runtime_smoke_integration_gate
from .gui_qt_runtime_smoke_integration_matrix import build_qt_runtime_smoke_integration_matrix
from .gui_qt_runtime_smoke_integration_report import build_qt_runtime_smoke_integration_report
from .gui_qt_runtime_smoke_integration_risk import build_qt_runtime_smoke_integration_risk
from .gui_qt_runtime_smoke_integration_snapshot import build_qt_runtime_smoke_integration_snapshot

QT_RUNTIME_SMOKE_INTEGRATION_BUNDLE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_integration_bundle(
    *,
    adapter_bundle: Mapping[str, object],
    page_handoff: Mapping[str, object],
    shell_bundle: Mapping[str, object],
) -> dict[str, object]:
    matrix = build_qt_runtime_smoke_integration_matrix(adapter_bundle=adapter_bundle, page_handoff=page_handoff, shell_bundle=shell_bundle)
    gate = evaluate_qt_runtime_smoke_integration_gate(matrix)
    checklist = build_qt_runtime_smoke_integration_checklist(gate)
    risk = build_qt_runtime_smoke_integration_risk(gate, checklist)
    report = build_qt_runtime_smoke_integration_report(matrix, gate, checklist, risk)
    snapshot = build_qt_runtime_smoke_integration_snapshot(report)
    return {
        "schema_version": QT_RUNTIME_SMOKE_INTEGRATION_BUNDLE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_integration_bundle",
        "matrix": matrix,
        "gate": gate,
        "checklist": checklist,
        "risk": risk,
        "report": report,
        "snapshot": snapshot,
        "ready_for_guarded_shell_wiring": bool(report.get("ready")),
        "summary": {
            "ready_for_guarded_shell_wiring": bool(report.get("ready")),
            "problem_count": report["summary"]["problem_count"],
            "failed_required_check_count": report["summary"]["failed_required_check_count"],
            "risk_level": report["summary"]["risk_level"],
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


__all__ = ["QT_RUNTIME_SMOKE_INTEGRATION_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_integration_bundle"]
