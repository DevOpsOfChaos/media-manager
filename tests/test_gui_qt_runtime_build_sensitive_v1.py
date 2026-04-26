from __future__ import annotations

from media_manager.core.gui_qt_runtime_build_steps import build_qt_runtime_build_plan
from media_manager.core.gui_qt_runtime_build_validator import validate_qt_runtime_build_plan


def test_runtime_build_plan_marks_sensitive_nodes_local_only() -> None:
    runtime_plan = {
        "root": {
            "id": "people-page",
            "source_component": "PeopleReviewPage",
            "supported_component": True,
            "qt_widget": "QWidget",
            "layout": "QVBoxLayout",
            "props": {"privacy_notice": "Face crops are sensitive local biometric data."},
            "children": [],
            "sensitive": True,
            "execute_policy": "none",
        }
    }

    build_plan = build_qt_runtime_build_plan(runtime_plan)
    sensitive_steps = [step for step in build_plan["steps"] if step["operation"] == "mark_sensitive"]

    assert build_plan["summary"]["sensitive_step_count"] == 1
    assert sensitive_steps[0]["privacy_policy"] == "local_only"
    assert sensitive_steps[0]["allows_export"] is False
    assert validate_qt_runtime_build_plan(build_plan)["valid"] is True
