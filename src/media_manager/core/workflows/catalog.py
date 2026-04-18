from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class WorkflowDefinition:
    name: str
    title: str
    summary: str
    best_for: str
    example_command: str
    delegated_command: str


@dataclass(slots=True, frozen=True)
class WorkflowProblem:
    name: str
    title: str
    summary: str
    recommended_workflow: str
    next_step: str


WORKFLOW_DEFINITIONS: tuple[WorkflowDefinition, ...] = (
    WorkflowDefinition(
        name="cleanup",
        title="Cleanup workflow",
        summary=(
            "Best entry point for multiple messy source folders where you want one guided overview "
            "covering scan, exact duplicates, organize planning, and rename planning."
        ),
        best_for="Mixed unsorted libraries with possible duplicates and inconsistent structure.",
        example_command=(
            "media-manager workflow run cleanup --source <A> --source <B> --target <TARGET> --json"
        ),
        delegated_command="cleanup",
    ),
    WorkflowDefinition(
        name="trip",
        title="Trip workflow",
        summary=(
            "Build or execute a date-range-based trip collection using hard links or copies."
        ),
        best_for="Vacation or event ranges where you want a dedicated collection folder.",
        example_command=(
            "media-manager workflow run trip --source <SOURCE> --target <TARGET> "
            "--label Italy_2025 --start 2025-08-01 --end 2025-08-14"
        ),
        delegated_command="trip",
    ),
    WorkflowDefinition(
        name="duplicates",
        title="Duplicates workflow",
        summary=(
            "Scan exact duplicates, optionally auto-pick a keep candidate, and inspect review data "
            "before any delete-oriented execution."
        ),
        best_for="Large libraries where deduplication is the immediate problem.",
        example_command=(
            "media-manager workflow run duplicates --source <SOURCE> --policy first --show-plan"
        ),
        delegated_command="duplicates",
    ),
    WorkflowDefinition(
        name="organize",
        title="Organize workflow",
        summary=(
            "Plan or apply target-folder organization based on resolved capture dates and directory patterns."
        ),
        best_for="Sorting media into a target library structure.",
        example_command=(
            "media-manager workflow run organize --source <SOURCE> --target <TARGET> --json"
        ),
        delegated_command="organize",
    ),
    WorkflowDefinition(
        name="rename",
        title="Rename workflow",
        summary=(
            "Plan or apply template-based file renames using resolved capture dates and source metadata."
        ),
        best_for="Standardizing file names after or before organization.",
        example_command=(
            "media-manager workflow run rename --source <SOURCE> --template "{date:%Y-%m-%d_%H-%M-%S}_{stem}""
        ),
        delegated_command="rename",
    ),
)

WORKFLOW_PROBLEMS: tuple[WorkflowProblem, ...] = (
    WorkflowProblem(
        name="messy-multi-source-library",
        title="Messy multi-source library",
        summary=(
            "You have several unsorted sources, probably duplicates, and want a guided first overview."
        ),
        recommended_workflow="cleanup",
        next_step=(
            "Start with the cleanup workflow in JSON mode, review duplicates and organize plans, then "
            "apply organize or rename step by step."
        ),
    ),
    WorkflowProblem(
        name="build-trip-collection",
        title="Build a trip collection",
        summary=(
            "You know the date range of a vacation or event and want a dedicated collection."
        ),
        recommended_workflow="trip",
        next_step=(
            "Run the trip workflow first as dry-run, verify the selected files, then apply with link or copy mode."
        ),
    ),
    WorkflowProblem(
        name="review-duplicates-first",
        title="Review duplicates first",
        summary=(
            "Duplicates are the biggest immediate problem and you want to inspect them before anything else."
        ),
        recommended_workflow="duplicates",
        next_step=(
            "Run duplicates with a keep policy and show-plan or similar-review options before any delete execution."
        ),
    ),
)


def list_workflows() -> list[WorkflowDefinition]:
    return list(WORKFLOW_DEFINITIONS)


def get_workflow_definition(name: str) -> WorkflowDefinition | None:
    normalized = name.strip().lower()
    for item in WORKFLOW_DEFINITIONS:
        if item.name == normalized:
            return item
    return None


def list_workflow_problems() -> list[WorkflowProblem]:
    return list(WORKFLOW_PROBLEMS)


def get_workflow_problem(name: str) -> WorkflowProblem | None:
    normalized = name.strip().lower()
    for item in WORKFLOW_PROBLEMS:
        if item.name == normalized:
            return item
    return None
