from media_manager.workflow_progress import (
    workflow_completed_steps,
    workflow_next_required_step,
    workflow_progress_percent,
    workflow_required_steps,
)


def test_workflow_required_steps_for_full_cleanup() -> None:
    assert workflow_required_steps("full_cleanup") == ["duplicates", "organize", "rename"]



def test_workflow_progress_ignores_skipped_non_required_steps() -> None:
    statuses = {
        "duplicates": "Skipped",
        "organize": "Done (10)",
        "rename": "Pending",
    }

    assert workflow_completed_steps("ready_for_sorting", statuses) == 1
    assert workflow_progress_percent("ready_for_sorting", statuses) == 50
    assert workflow_next_required_step("ready_for_sorting", statuses) == "rename"



def test_workflow_progress_finishes_for_rename_only() -> None:
    statuses = {
        "duplicates": "Skipped",
        "organize": "Skipped",
        "rename": "Done (8)",
    }

    assert workflow_completed_steps("ready_for_rename", statuses) == 1
    assert workflow_progress_percent("ready_for_rename", statuses) == 100
    assert workflow_next_required_step("ready_for_rename", statuses) == "finished"
