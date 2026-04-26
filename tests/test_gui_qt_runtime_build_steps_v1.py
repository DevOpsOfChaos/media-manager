from __future__ import annotations

from media_manager.core.gui_qt_runtime_build_steps import build_qt_runtime_build_plan, collect_runtime_build_step_ids


def _runtime_plan() -> dict[str, object]:
    return {
        "kind": "qt_runtime_widget_plan",
        "root": {
            "id": "shell",
            "source_component": "ShellFrame",
            "supported_component": True,
            "qt_widget": "QWidget",
            "layout": "QHBoxLayout",
            "props": {"title": "Media Manager"},
            "children": [
                {
                    "id": "nav",
                    "source_component": "NavigationRail",
                    "supported_component": True,
                    "qt_widget": "QFrame",
                    "layout": "QVBoxLayout",
                    "props": {"item_count": 2},
                    "children": [],
                    "sensitive": False,
                    "execute_policy": "none",
                }
            ],
            "sensitive": False,
            "execute_policy": "none",
        },
    }


def test_runtime_build_plan_creates_deterministic_steps() -> None:
    plan = build_qt_runtime_build_plan(_runtime_plan())

    ids = collect_runtime_build_step_ids(plan)

    assert plan["kind"] == "qt_runtime_build_plan"
    assert ids[:3] == ["create-shell", "layout-shell", "props-shell"]
    assert "attach-nav" in ids
    assert plan["summary"]["node_count"] == 2
    assert plan["summary"]["operation_counts"]["create_widget"] == 2
    assert plan["capabilities"]["requires_pyside6"] is False
    assert plan["capabilities"]["opens_window"] is False
