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

from media_manager.core.gui_qt_runtime_node_trace import build_qt_runtime_node_trace, build_qt_runtime_sensitive_node_traces


def test_runtime_node_trace_preserves_sensitive_deferred_sequence() -> None:
    trace = build_qt_runtime_node_trace(sample_build_plan(), "face-1")

    assert trace["creates_widget"] is True
    assert trace["attached_to_parent"] is True
    assert trace["marked_sensitive"] is True
    assert trace["local_only"] is True
    assert trace["deferred_execution_count"] == 1
    assert trace["operations"] == [
        "create_widget",
        "apply_props",
        "mark_sensitive",
        "connect_bindings",
        "attach_child",
    ]


def test_sensitive_node_traces_collect_local_only_nodes() -> None:
    traces = build_qt_runtime_sensitive_node_traces(sample_build_plan())

    assert traces["summary"]["trace_count"] == 1
    assert traces["summary"]["marked_sensitive_count"] == 1
    assert traces["traces"][0]["node_id"] == "face-1"
