from __future__ import annotations

from collections.abc import Mapping

from .gui_qt_runtime_smoke_desktop_acceptance_action_plan import build_qt_runtime_smoke_desktop_acceptance_action_plan
from .gui_qt_runtime_smoke_desktop_acceptance_audit import audit_qt_runtime_smoke_desktop_acceptance
from .gui_qt_runtime_smoke_desktop_acceptance_checklist import build_qt_runtime_smoke_desktop_acceptance_checklist
from .gui_qt_runtime_smoke_desktop_acceptance_dashboard import build_qt_runtime_smoke_desktop_acceptance_dashboard
from .gui_qt_runtime_smoke_desktop_acceptance_evidence_policy import build_qt_runtime_smoke_desktop_acceptance_evidence_policy
from .gui_qt_runtime_smoke_desktop_acceptance_gate import build_qt_runtime_smoke_desktop_acceptance_gate
from .gui_qt_runtime_smoke_desktop_acceptance_history_index import build_qt_runtime_smoke_desktop_acceptance_history_index
from .gui_qt_runtime_smoke_desktop_acceptance_input import build_qt_runtime_smoke_desktop_acceptance_input
from .gui_qt_runtime_smoke_desktop_acceptance_issue_triage import build_qt_runtime_smoke_desktop_acceptance_issue_triage
from .gui_qt_runtime_smoke_desktop_acceptance_manifest import build_qt_runtime_smoke_desktop_acceptance_manifest
from .gui_qt_runtime_smoke_desktop_acceptance_matrix import build_qt_runtime_smoke_desktop_acceptance_matrix
from .gui_qt_runtime_smoke_desktop_acceptance_operator_replay import build_qt_runtime_smoke_desktop_acceptance_operator_replay
from .gui_qt_runtime_smoke_desktop_acceptance_quality import build_qt_runtime_smoke_desktop_acceptance_quality
from .gui_qt_runtime_smoke_desktop_acceptance_redaction import build_qt_runtime_smoke_desktop_acceptance_redaction
from .gui_qt_runtime_smoke_desktop_acceptance_regression import build_qt_runtime_smoke_desktop_acceptance_regression
from .gui_qt_runtime_smoke_desktop_acceptance_release_note import build_qt_runtime_smoke_desktop_acceptance_release_note
from .gui_qt_runtime_smoke_desktop_acceptance_rollout_plan import build_qt_runtime_smoke_desktop_acceptance_rollout_plan
from .gui_qt_runtime_smoke_desktop_acceptance_snapshot import build_qt_runtime_smoke_desktop_acceptance_snapshot
from .gui_qt_runtime_smoke_desktop_acceptance_trend import build_qt_runtime_smoke_desktop_acceptance_trend

QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_BUNDLE_SCHEMA_VERSION = "1.0"


def build_qt_runtime_smoke_desktop_acceptance_bundle(
    result_bundle: Mapping[str, object],
    start_bundle: Mapping[str, object],
    *,
    history_entries: list[Mapping[str, object]] | None = None,
) -> dict[str, object]:
    acceptance_input = build_qt_runtime_smoke_desktop_acceptance_input(result_bundle, start_bundle)
    matrix = build_qt_runtime_smoke_desktop_acceptance_matrix(acceptance_input)
    gate = build_qt_runtime_smoke_desktop_acceptance_gate(matrix)
    quality = build_qt_runtime_smoke_desktop_acceptance_quality(acceptance_input, gate)
    history = build_qt_runtime_smoke_desktop_acceptance_history_index(history_entries)
    regression = build_qt_runtime_smoke_desktop_acceptance_regression(history, gate)
    trend = build_qt_runtime_smoke_desktop_acceptance_trend(history)
    policy = build_qt_runtime_smoke_desktop_acceptance_evidence_policy()
    export_payload = result_bundle.get("export") if isinstance(result_bundle.get("export"), Mapping) else {}
    redaction = build_qt_runtime_smoke_desktop_acceptance_redaction(export_payload)
    replay = build_qt_runtime_smoke_desktop_acceptance_operator_replay(result_bundle)
    triage = build_qt_runtime_smoke_desktop_acceptance_issue_triage(result_bundle)
    actions = build_qt_runtime_smoke_desktop_acceptance_action_plan(gate, triage)
    rollout = build_qt_runtime_smoke_desktop_acceptance_rollout_plan(gate, quality)
    release_note = build_qt_runtime_smoke_desktop_acceptance_release_note(gate, quality)
    checklist = build_qt_runtime_smoke_desktop_acceptance_checklist(gate, redaction)
    dashboard = build_qt_runtime_smoke_desktop_acceptance_dashboard(gate, quality, trend, triage)
    audit = audit_qt_runtime_smoke_desktop_acceptance(gate, checklist, policy, redaction)
    accepted = bool(gate.get("ready")) and bool(audit.get("valid"))
    bundle: dict[str, object] = {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_BUNDLE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_acceptance_bundle",
        "acceptance_input": acceptance_input,
        "matrix": matrix,
        "gate": gate,
        "quality": quality,
        "history": history,
        "regression": regression,
        "trend": trend,
        "evidence_policy": policy,
        "redaction": redaction,
        "operator_replay": replay,
        "issue_triage": triage,
        "action_plan": actions,
        "rollout_plan": rollout,
        "release_note": release_note,
        "checklist": checklist,
        "dashboard": dashboard,
        "audit": audit,
        "accepted": accepted,
        "summary": {
            "accepted": accepted,
            "quality_level": quality["level"],
            "problem_count": int(gate.get("problem_count") or 0) + int(audit.get("problem_count") or 0),
            "issue_count": dashboard["summary"]["issue_count"],
            "regressed": regression["regressed"],
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }
    bundle["manifest"] = build_qt_runtime_smoke_desktop_acceptance_manifest(bundle["summary"])
    bundle["snapshot"] = build_qt_runtime_smoke_desktop_acceptance_snapshot(bundle)
    return bundle


__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ACCEPTANCE_BUNDLE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_acceptance_bundle"]
