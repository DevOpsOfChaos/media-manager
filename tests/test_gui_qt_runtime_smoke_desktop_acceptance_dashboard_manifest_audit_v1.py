from __future__ import annotations


def sample_result_bundle(*, accepted: bool = True, problem_count: int = 0, sensitive: bool = False) -> dict[str, object]:
    results = [
        {"check_id": "read-command", "passed": True, "required": True, "has_evidence_path": False, "contains_sensitive_media": False},
        {"check_id": "confirm-local-only", "passed": True, "required": True, "has_evidence_path": False, "contains_sensitive_media": sensitive},
        {"check_id": "confirm-window-title", "passed": accepted, "required": True, "has_evidence_path": True, "contains_sensitive_media": False},
        {"check_id": "confirm-active-page", "passed": True, "required": True, "has_evidence_path": False, "contains_sensitive_media": False},
        {"check_id": "confirm-no-auto-apply", "passed": True, "required": True, "has_evidence_path": False, "contains_sensitive_media": False},
    ]
    return {
        "kind": "qt_runtime_smoke_desktop_result_bundle",
        "accepted": accepted,
        "summary": {
            "accepted": accepted,
            "decision": "accepted" if accepted else "blocked",
            "result_count": 5,
            "problem_count": problem_count,
            "failed_required_count": 0 if accepted else 1,
            "missing_required_count": 0,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "validation": {"results": results},
        "audit": {"problems": [] if problem_count == 0 else [{"code": "failed_required_result", "check_id": "confirm-window-title"}]},
        "export": {"results": results, "summary": {"accepted": accepted}},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }


def sample_start_bundle(*, ready: bool = True, problem_count: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_start_bundle",
        "ready_for_manual_desktop_start": ready,
        "summary": {
            "ready_for_manual_desktop_start": ready,
            "problem_count": problem_count,
            "opens_window": False,
            "executes_commands": False,
            "local_only": True,
        },
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }


def sample_history() -> list[dict[str, object]]:
    return [
        {"recorded_at_utc": "2026-04-27T19:00:00Z", "accepted": True, "problem_count": 0},
        {"recorded_at_utc": "2026-04-27T20:00:00Z", "accepted": True, "problem_count": 0},
    ]

from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_audit import audit_qt_runtime_smoke_desktop_acceptance
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_bundle import build_qt_runtime_smoke_desktop_acceptance_bundle
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_dashboard import build_qt_runtime_smoke_desktop_acceptance_dashboard
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_manifest import build_qt_runtime_smoke_desktop_acceptance_manifest


def test_dashboard_manifest_and_audit_for_clean_acceptance() -> None:
    bundle = build_qt_runtime_smoke_desktop_acceptance_bundle(sample_result_bundle(), sample_start_bundle(), history_entries=sample_history())
    dashboard = build_qt_runtime_smoke_desktop_acceptance_dashboard(bundle["gate"], bundle["quality"], bundle["trend"], bundle["issue_triage"])
    manifest = build_qt_runtime_smoke_desktop_acceptance_manifest(bundle["summary"], recorded_at_utc="2026-04-27T21:00:00Z")
    audit = audit_qt_runtime_smoke_desktop_acceptance(bundle["gate"], bundle["checklist"], bundle["evidence_policy"], bundle["redaction"])

    assert dashboard["summary"]["card_count"] == 4
    assert dashboard["summary"]["issue_count"] == 0
    assert manifest["privacy"]["metadata_only"] is True
    assert audit["valid"] is True
