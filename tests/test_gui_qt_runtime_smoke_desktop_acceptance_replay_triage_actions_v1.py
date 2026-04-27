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

from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_action_plan import build_qt_runtime_smoke_desktop_acceptance_action_plan
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_gate import build_qt_runtime_smoke_desktop_acceptance_gate
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_input import build_qt_runtime_smoke_desktop_acceptance_input
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_issue_triage import build_qt_runtime_smoke_desktop_acceptance_issue_triage
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_matrix import build_qt_runtime_smoke_desktop_acceptance_matrix
from media_manager.core.gui_qt_runtime_smoke_desktop_acceptance_operator_replay import build_qt_runtime_smoke_desktop_acceptance_operator_replay


def test_replay_triage_and_actions_for_clean_bundle() -> None:
    result = sample_result_bundle()
    gate = build_qt_runtime_smoke_desktop_acceptance_gate(build_qt_runtime_smoke_desktop_acceptance_matrix(build_qt_runtime_smoke_desktop_acceptance_input(result, sample_start_bundle())))
    replay = build_qt_runtime_smoke_desktop_acceptance_operator_replay(result)
    triage = build_qt_runtime_smoke_desktop_acceptance_issue_triage(result)
    actions = build_qt_runtime_smoke_desktop_acceptance_action_plan(gate, triage)

    assert replay["summary"]["step_count"] == 5
    assert replay["summary"]["immediate_execution_count"] == 0
    assert triage["summary"]["issue_count"] == 0
    assert actions["summary"]["confirmation_action_count"] == 2
    assert actions["summary"]["immediate_execution_count"] == 0
