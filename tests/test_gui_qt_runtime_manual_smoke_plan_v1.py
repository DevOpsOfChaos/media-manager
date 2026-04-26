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
from media_manager.core.gui_qt_runtime_manual_smoke_plan import build_qt_runtime_manual_smoke_plan


def test_manual_smoke_plan_adds_people_privacy_checks_in_german() -> None:
    manifest = build_qt_runtime_handoff_manifest(sample_readiness_report())
    plan = build_qt_runtime_manual_smoke_plan(manifest, language="de")

    labels = [check["label"] for check in plan["checks"]]

    assert plan["language"] == "de"
    assert plan["summary"]["contains_sensitive_people_data"] is True
    assert plan["summary"]["privacy_check_count"] >= 3
    assert any("People Review" in label for label in labels)
    assert any("Face-Assets" in label for label in labels)
    assert plan["capabilities"]["requires_pyside6"] is False
