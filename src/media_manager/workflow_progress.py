from __future__ import annotations

from collections.abc import Mapping

REQUIRED_STEPS_BY_PROBLEM: dict[str, list[str]] = {
    "full_cleanup": ["duplicates", "organize", "rename"],
    "ready_for_sorting": ["organize", "rename"],
    "ready_for_rename": ["rename"],
    "exact_duplicates_only": ["duplicates"],
}


def workflow_required_steps(problem_key: str) -> list[str]:
    return list(REQUIRED_STEPS_BY_PROBLEM.get(problem_key, REQUIRED_STEPS_BY_PROBLEM["full_cleanup"]))


def workflow_completed_steps(problem_key: str, statuses: Mapping[str, str]) -> int:
    count = 0
    for step in workflow_required_steps(problem_key):
        if statuses.get(step, "").startswith("Done"):
            count += 1
    return count


def workflow_progress_percent(problem_key: str, statuses: Mapping[str, str]) -> int:
    required_steps = workflow_required_steps(problem_key)
    if not required_steps:
        return 0
    return int((workflow_completed_steps(problem_key, statuses) / len(required_steps)) * 100)


def workflow_next_required_step(problem_key: str, statuses: Mapping[str, str]) -> str:
    for step in workflow_required_steps(problem_key):
        if not statuses.get(step, "").startswith("Done"):
            return step
    return "finished"
