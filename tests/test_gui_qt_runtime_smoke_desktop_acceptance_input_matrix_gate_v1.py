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

from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_gate import build_qt_runtime_smoke_desktop_acceptance_gate
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_input import build_qt_runtime_smoke_desktop_acceptance_input
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_matrix import build_qt_runtime_smoke_desktop_acceptance_matrix


def test_acceptance_input_matrix_and_gate_accept_clean_desktop_result() -> None:
    acceptance_input = build_qt_runtime_smoke_desktop_acceptance_input(sample_result_bundle(), sample_start_bundle())
    matrix = build_qt_runtime_smoke_desktop_acceptance_matrix(acceptance_input)
    gate = build_qt_runtime_smoke_desktop_acceptance_gate(matrix)

    assert acceptance_input["summary"]["accepted"] is True
    assert matrix["summary"]["row_count"] == 6
    assert matrix["summary"]["failed_required_count"] == 0
    assert gate["ready"] is True
    assert gate["decision"] == "accepted_for_guarded_desktop_runtime"


def test_acceptance_gate_blocks_failed_result() -> None:
    acceptance_input = build_qt_runtime_smoke_desktop_acceptance_input(sample_result_bundle(accepted=False, problem_count=1), sample_start_bundle())
    matrix = build_qt_runtime_smoke_desktop_acceptance_matrix(acceptance_input)
    gate = build_qt_runtime_smoke_desktop_acceptance_gate(matrix)

    assert gate["ready"] is False
    assert gate["problem_count"] == 1
