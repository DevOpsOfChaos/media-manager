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
from media_manager.core.gui_qt_runtime_launch_contract import (
    build_qt_runtime_launch_contract,
    summarize_qt_runtime_launch_contract,
)


def test_launch_contract_is_manual_only_and_does_not_open_window() -> None:
    manifest = build_qt_runtime_handoff_manifest(sample_readiness_report())
    contract = build_qt_runtime_launch_contract(manifest, language="de", theme="modern-dark")

    assert contract["ready_for_launch_attempt"] is True
    assert contract["argv"][:3] == ["media-manager-gui", "--active-page", "people-review"]
    assert "--language" in contract["argv"]
    assert "de" in contract["argv"]
    assert contract["execution_policy"]["mode"] == "manual_only"
    assert contract["execution_policy"]["executes_immediately"] is False
    assert contract["execution_policy"]["opens_window"] is False
    assert contract["runtime_requirements"]["requires_pyside6_to_open_window"] is True
    assert "Execution mode: manual_only" in summarize_qt_runtime_launch_contract(contract)
