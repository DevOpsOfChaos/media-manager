from media_manager.core.gui_qt_batch_action_panel import batch_action_summary, build_batch_action_panel
from media_manager.core.gui_qt_job_launcher_plan import build_job_launcher_plan, launcher_plan_summary


def test_batch_action_panel_blocks_without_selection_and_marks_risk() -> None:
    panel = build_batch_action_panel(selected_count=0, action_ids=["accept_selected", "apply_selected"])
    assert panel["enabled_action_count"] == 0
    assert panel["confirmation_action_count"] == 1
    assert all(action["executes_immediately"] is False for action in panel["actions"])
    assert batch_action_summary(panel)["selected_count"] == 0


def test_job_launcher_plan_requires_confirmation_for_apply() -> None:
    plan = build_job_launcher_plan(["media-manager", "people", "review-apply", "--apply"])
    assert plan["risk_level"] == "high"
    assert plan["can_launch"] is False
    assert plan["requires_confirmation"] is True
    assert launcher_plan_summary(plan)["arg_count"] == 4
    confirmed = build_job_launcher_plan(plan["argv"], confirmed=True)
    assert confirmed["can_launch"] is True
    assert confirmed["executes_immediately"] is False
