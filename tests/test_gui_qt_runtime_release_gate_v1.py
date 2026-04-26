from __future__ import annotations


def sample_readiness_report() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "kind": "qt_runtime_readiness_report",
        "active_page_id": "people-review",
        "ready": True,
        "summary": {
            "step_count": 12,
            "node_count": 5,
            "operation_count": 5,
            "sensitive_node_count": 2,
            "local_only_node_count": 2,
            "deferred_execution_count": 1,
            "safety_problem_count": 0,
            "validation_problem_count": 0,
            "ready": True,
        },
        "safety_audit": {
            "valid": True,
            "problem_count": 0,
            "summary": {
                "sensitive_node_count": 2,
                "local_only_node_count": 2,
                "deferred_execution_count": 1,
            },
        },
        "validation": {"valid": True, "problem_count": 0},
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }

from media_manager.core.gui_qt_runtime_handoff_manifest import build_qt_runtime_handoff_manifest
from media_manager.core.gui_qt_runtime_launch_contract import build_qt_runtime_launch_contract
from media_manager.core.gui_qt_runtime_manual_smoke_plan import build_qt_runtime_manual_smoke_plan
from media_manager.core.gui_qt_runtime_release_gate import evaluate_qt_runtime_release_gate


def test_release_gate_ready_for_manual_smoke_but_not_complete_without_results() -> None:
    manifest = build_qt_runtime_handoff_manifest(sample_readiness_report())
    contract = build_qt_runtime_launch_contract(manifest)
    smoke_plan = build_qt_runtime_manual_smoke_plan(manifest)

    gate = evaluate_qt_runtime_release_gate(manifest, contract, smoke_plan)

    assert gate["ready_for_manual_smoke"] is True
    assert gate["manual_smoke_complete"] is False
    assert gate["summary"]["missing_smoke_check_count"] == smoke_plan["summary"]["required_check_count"]


def test_release_gate_completes_when_all_required_smoke_results_pass() -> None:
    manifest = build_qt_runtime_handoff_manifest(sample_readiness_report())
    contract = build_qt_runtime_launch_contract(manifest)
    smoke_plan = build_qt_runtime_manual_smoke_plan(manifest)
    results = {check["id"]: True for check in smoke_plan["checks"] if check["required"]}

    gate = evaluate_qt_runtime_release_gate(manifest, contract, smoke_plan, smoke_results=results)

    assert gate["ready_for_manual_smoke"] is True
    assert gate["manual_smoke_complete"] is True
    assert gate["missing_smoke_checks"] == []
