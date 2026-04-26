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

from media_manager.core.gui_qt_runtime_handoff_manifest import (
    build_qt_runtime_handoff_manifest,
    summarize_qt_runtime_handoff_manifest,
)


def test_handoff_manifest_preserves_readiness_and_privacy() -> None:
    manifest = build_qt_runtime_handoff_manifest(sample_readiness_report())

    assert manifest["kind"] == "qt_runtime_handoff_manifest"
    assert manifest["active_page_id"] == "people-review"
    assert manifest["ready_for_manual_smoke"] is True
    assert manifest["readiness"]["sensitive_node_count"] == 2
    assert manifest["privacy"]["contains_sensitive_people_data"] is True
    assert manifest["privacy"]["network_required"] is False
    assert manifest["runtime_requirements"]["requires_pyside6_to_build_manifest"] is False
    assert "Sensitive people data: True" in summarize_qt_runtime_handoff_manifest(manifest)
