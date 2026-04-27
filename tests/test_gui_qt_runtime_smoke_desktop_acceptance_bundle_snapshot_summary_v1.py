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

from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_bundle import build_qt_runtime_smoke_desktop_acceptance_bundle
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_snapshot import build_qt_runtime_smoke_desktop_acceptance_snapshot
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_summary import summarize_qt_runtime_smoke_desktop_acceptance_bundle


def test_acceptance_bundle_snapshot_and_summary_for_clean_result() -> None:
    bundle = build_qt_runtime_smoke_desktop_acceptance_bundle(sample_result_bundle(), sample_start_bundle(), history_entries=sample_history())
    snapshot_a = build_qt_runtime_smoke_desktop_acceptance_snapshot(bundle)
    snapshot_b = build_qt_runtime_smoke_desktop_acceptance_snapshot(bundle)
    text = summarize_qt_runtime_smoke_desktop_acceptance_bundle(bundle)

    assert bundle["accepted"] is True
    assert bundle["summary"]["quality_level"] == "excellent"
    assert bundle["snapshot"]["payload_hash"] == snapshot_a["payload_hash"]
    assert snapshot_a["payload_hash"] == snapshot_b["payload_hash"]
    assert len(snapshot_a["payload_hash"]) == 64
    assert "Accepted: True" in text


def test_acceptance_bundle_blocks_failed_result_and_detects_regression() -> None:
    bundle = build_qt_runtime_smoke_desktop_acceptance_bundle(sample_result_bundle(accepted=False, problem_count=1), sample_start_bundle(), history_entries=sample_history())

    assert bundle["accepted"] is False
    assert bundle["summary"]["problem_count"] > 0
    assert bundle["summary"]["regressed"] is True
