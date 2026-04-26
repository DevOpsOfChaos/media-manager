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

from media_manager.core.gui_qt_runtime_safety_audit import audit_qt_runtime_build_safety


def test_runtime_safety_audit_accepts_local_deferred_sensitive_steps() -> None:
    audit = audit_qt_runtime_build_safety(sample_build_plan())

    assert audit["valid"] is True
    assert audit["problem_count"] == 0
    assert audit["summary"]["sensitive_node_count"] == 1
    assert audit["summary"]["unsafe_immediate_execution_count"] == 0


def test_runtime_safety_audit_rejects_immediate_execution_and_missing_marker() -> None:
    plan = sample_build_plan()
    steps = list(plan["steps"])
    steps = [step for step in steps if step["operation"] != "mark_sensitive"]
    steps.append(
        {
            "step_id": "unsafe-action",
            "order": 8,
            "operation": "connect_bindings",
            "node_id": "face-1",
            "execute_policy": "immediate",
            "local_only": False,
        }
    )
    plan["steps"] = steps

    audit = audit_qt_runtime_build_safety(plan)

    assert audit["valid"] is False
    codes = {problem["code"] for problem in audit["problems"]}
    assert "unsafe_execute_policy" in codes
    assert "missing_sensitive_marker" in codes
