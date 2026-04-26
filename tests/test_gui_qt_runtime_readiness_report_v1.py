from __future__ import annotations


def sample_build_plan() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "kind": "qt_runtime_build_plan",
        "root_id": "root",
        "steps": [
            {
                "step_id": "create-root",
                "order": 1,
                "operation": "create_widget",
                "node_id": "root",
                "qt_widget": "QFrame",
                "supported_component": True,
                "execute_policy": "none",
                "local_only": False,
            },
            {
                "step_id": "layout-root",
                "order": 2,
                "operation": "configure_layout",
                "node_id": "root",
                "layout": "QVBoxLayout",
                "execute_policy": "none",
                "local_only": False,
            },
            {
                "step_id": "create-face-1",
                "order": 3,
                "operation": "create_widget",
                "node_id": "face-1",
                "parent_id": "root",
                "qt_widget": "QFrame",
                "supported_component": True,
                "sensitive": True,
                "execute_policy": "none",
                "local_only": True,
            },
            {
                "step_id": "props-face-1",
                "order": 4,
                "operation": "apply_props",
                "node_id": "face-1",
                "prop_keys": ["face_id", "asset_ref"],
                "execute_policy": "none",
                "local_only": True,
            },
            {
                "step_id": "sensitive-face-1",
                "order": 5,
                "operation": "mark_sensitive",
                "node_id": "face-1",
                "privacy_policy": "local_only",
                "execute_policy": "none",
                "local_only": True,
            },
            {
                "step_id": "bindings-face-1",
                "order": 6,
                "operation": "connect_bindings",
                "node_id": "face-1",
                "binding_keys": ["open_review"],
                "execute_policy": "deferred",
                "local_only": True,
            },
            {
                "step_id": "attach-face-1",
                "order": 7,
                "operation": "attach_child",
                "node_id": "face-1",
                "parent_id": "root",
                "execute_policy": "none",
                "local_only": True,
            },
        ],
        "summary": {"step_count": 7, "node_count": 2},
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
    }

from media_manager.core.gui_qt_runtime_readiness_report import (
    build_qt_runtime_readiness_report,
    summarize_qt_runtime_readiness_report,
)


def test_runtime_readiness_report_summarizes_bootstrap_build_plan() -> None:
    bootstrap = {
        "kind": "qt_runtime_bootstrap_plan",
        "active_page_id": "people-review",
        "ready": True,
        "build_plan": sample_build_plan(),
        "validation": {"valid": True, "problem_count": 0},
        "summary": {"active_page_id": "people-review"},
    }

    report = build_qt_runtime_readiness_report(bootstrap)

    assert report["ready"] is True
    assert report["active_page_id"] == "people-review"
    assert report["summary"]["step_count"] == 7
    assert report["summary"]["sensitive_node_count"] == 1
    assert report["capabilities"]["requires_pyside6"] is False
    assert "Ready: True" in summarize_qt_runtime_readiness_report(report)


def test_runtime_readiness_report_marks_validation_problems_not_ready() -> None:
    bootstrap = {
        "kind": "qt_runtime_bootstrap_plan",
        "active_page_id": "dashboard",
        "ready": True,
        "build_plan": sample_build_plan(),
        "validation": {"valid": False, "problem_count": 1},
    }

    report = build_qt_runtime_readiness_report(bootstrap)

    assert report["ready"] is False
    assert report["summary"]["validation_problem_count"] == 1
