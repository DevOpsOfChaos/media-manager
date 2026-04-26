from media_manager.core.gui_process_plan import build_process_plan, process_plan_from_job, validate_process_plan


def test_process_plan_is_non_shell_and_non_executing() -> None:
    plan = build_process_plan(command_argv=["media-manager", "people", "backend"], cwd=".")
    assert plan["shell"] is False
    assert plan["executes_immediately"] is False
    assert validate_process_plan(plan)["valid"] is True


def test_process_plan_from_job_keeps_context() -> None:
    plan = process_plan_from_job({"job_id": "j1", "action_id": "preview", "command_argv": ["media-manager", "doctor"], "risk_level": "safe"})
    assert plan["job_id"] == "j1"
    assert plan["program"] == "media-manager"
