from __future__ import annotations

from media_manager.core.gui_qt_runtime_build_steps import build_qt_runtime_build_plan
from media_manager.core.gui_qt_runtime_build_validator import validate_qt_runtime_build_plan


def _plan() -> dict[str, object]:
    return build_qt_runtime_build_plan(
        {
            "root": {
                "id": "root",
                "source_component": "ShellFrame",
                "supported_component": True,
                "qt_widget": "QWidget",
                "layout": "QVBoxLayout",
                "children": [],
                "execute_policy": "none",
            }
        }
    )


def test_runtime_build_validator_accepts_safe_plan() -> None:
    validation = validate_qt_runtime_build_plan(_plan())

    assert validation["valid"] is True
    assert validation["problem_count"] == 0


def test_runtime_build_validator_rejects_duplicate_steps() -> None:
    plan = _plan()
    steps = plan["steps"]
    steps.append(dict(steps[0]))

    validation = validate_qt_runtime_build_plan(plan)

    assert validation["valid"] is False
    assert any(problem.startswith("duplicate_step_id:") for problem in validation["problems"])
