from media_manager.core.gui_qt_workspace_flow import build_workspace_flow
from media_manager.core.gui_qt_workspace_guard import build_workspace_guard


def test_workspace_guard_warns_about_unsaved_changes() -> None:
    state = {
        "save_state": {"has_workspace_path": True, "has_unsaved_changes": True},
        "apply_preview": {"safe_to_apply": True, "blocked_reasons": []},
    }
    guard = build_workspace_guard(state)
    assert guard["warning_count"] == 1
    assert guard["can_close_without_prompt"] is False
    assert guard["can_apply"] is True


def test_workspace_flow_reports_blocked_next_step() -> None:
    state = {
        "save_state": {"has_workspace_path": False, "has_unsaved_changes": True, "pending_change_count": 1},
        "apply_preview": {"safe_to_apply": False, "blocked_reasons": ["groups_need_name"]},
        "guard": {"problem_count": 1, "problems": ["groups_need_name"]},
    }
    flow = build_workspace_flow(state)
    assert flow["blocked"] is True
    assert flow["next_step_id"] in {"load_workspace", "save_workspace", "apply_ready"}
