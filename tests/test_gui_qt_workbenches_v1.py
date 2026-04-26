from media_manager.core.gui_qt_profile_workbench import build_profile_workbench
from media_manager.core.gui_qt_run_history_workbench import build_run_history_workbench


def test_profile_workbench_selects_first_and_counts_invalid() -> None:
    workbench = build_profile_workbench([
        {"profile_id": "p1", "title": "People", "command": "people", "favorite": True},
        {"profile_id": "p2", "valid": False, "problem_count": 2},
    ])
    assert workbench["profile_count"] == 2
    assert workbench["favorite_count"] == 1
    assert workbench["invalid_count"] == 1
    assert workbench["selected_profile_id"] == "p1"


def test_run_history_workbench_filters_and_marks_attention() -> None:
    workbench = build_run_history_workbench([
        {"run_id": "r1", "status": "ok", "exit_code": 0},
        {"run_id": "r2", "status": "failed", "exit_code": 1},
        {"run_id": "r3", "status": "failed", "exit_code": 0},
    ], status_filter="failed")
    assert workbench["run_count"] == 2
    assert workbench["attention_count"] == 2
    assert workbench["rows"][0]["run_id"] == "r2"
