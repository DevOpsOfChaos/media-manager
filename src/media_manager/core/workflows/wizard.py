from __future__ import annotations

from dataclasses import dataclass, field

from .catalog import WorkflowDefinition, WorkflowProblem, get_workflow_definition, get_workflow_problem


@dataclass(slots=True, frozen=True)
class WorkflowCommandSuggestion:
    title: str
    command: str


@dataclass(slots=True)
class WorkflowWizardResult:
    recommended_workflow: WorkflowDefinition
    matched_problem: WorkflowProblem | None
    confidence: str
    reason: str
    notes: list[str] = field(default_factory=list)
    command_suggestions: list[WorkflowCommandSuggestion] = field(default_factory=list)


def _build_command_suggestions(workflow_name: str) -> list[WorkflowCommandSuggestion]:
    if workflow_name == "cleanup":
        return [
            WorkflowCommandSuggestion(
                title="Dry-run cleanup overview",
                command="media-manager workflow run cleanup --source <A> --source <B> --target <TARGET> --json",
            ),
            WorkflowCommandSuggestion(
                title="Apply only organize step later",
                command="media-manager workflow run cleanup --source <A> --source <B> --target <TARGET> --apply-organize --journal <JOURNAL.json>",
            ),
        ]
    if workflow_name == "trip":
        return [
            WorkflowCommandSuggestion(
                title="Preview trip selection",
                command=(
                    "media-manager workflow run trip --source <SOURCE> --target <TARGET> "
                    "--label Italy_2025 --start 2025-08-01 --end 2025-08-14 --json"
                ),
            ),
            WorkflowCommandSuggestion(
                title="Apply trip collection with links",
                command=(
                    "media-manager workflow run trip --source <SOURCE> --target <TARGET> "
                    "--label Italy_2025 --start 2025-08-01 --end 2025-08-14 --apply"
                ),
            ),
        ]
    if workflow_name == "duplicates":
        return [
            WorkflowCommandSuggestion(
                title="Exact duplicate review",
                command="media-manager workflow run duplicates --source <SOURCE> --policy first --show-plan",
            ),
            WorkflowCommandSuggestion(
                title="Similar image review",
                command="media-manager workflow run duplicates --source <SOURCE> --similar-images --show-similar-review",
            ),
        ]
    if workflow_name == "rename":
        return [
            WorkflowCommandSuggestion(
                title="Rename dry-run",
                command=(
                    'media-manager workflow run rename --source <SOURCE> --template "{date:%Y-%m-%d_%H-%M-%S}_{stem}" --json'
                ),
            ),
            WorkflowCommandSuggestion(
                title="Apply renames with journal",
                command=(
                    'media-manager workflow run rename --source <SOURCE> --template "{date:%Y-%m-%d_%H-%M-%S}_{stem}" --apply --journal <JOURNAL.json>'
                ),
            ),
        ]
    return [
        WorkflowCommandSuggestion(
            title="Organize dry-run",
            command="media-manager workflow run organize --source <SOURCE> --target <TARGET> --json",
        ),
        WorkflowCommandSuggestion(
            title="Apply organize step",
            command="media-manager workflow run organize --source <SOURCE> --target <TARGET> --apply --journal <JOURNAL.json>",
        ),
    ]


def build_workflow_wizard_result(
    *,
    problem: str | None = None,
    source_count: int = 1,
    has_duplicates: bool = False,
    date_range_known: bool = False,
    wants_trip: bool = False,
    wants_rename: bool = False,
    wants_organization: bool = False,
) -> WorkflowWizardResult:
    matched_problem = get_workflow_problem(problem) if problem else None
    notes: list[str] = []

    if matched_problem is not None:
        workflow = get_workflow_definition(matched_problem.recommended_workflow)
        if workflow is None:
            raise RuntimeError(f"Catalog inconsistency: missing workflow {matched_problem.recommended_workflow}")
        confidence = "high"
        reason = matched_problem.summary
        notes.append(matched_problem.next_step)
        if workflow.name == "trip" and not date_range_known:
            confidence = "medium"
            notes.append("You chose a trip-style problem, but you still need a reliable date range before execution.")
        return WorkflowWizardResult(
            recommended_workflow=workflow,
            matched_problem=matched_problem,
            confidence=confidence,
            reason=reason,
            notes=notes,
            command_suggestions=_build_command_suggestions(workflow.name),
        )

    if wants_trip or date_range_known:
        workflow = get_workflow_definition("trip")
        if workflow is None:
            raise RuntimeError("Catalog inconsistency: missing trip workflow")
        confidence = "high" if date_range_known else "medium"
        reason = "A date-range based collection is the clearest next step for the information you provided."
        if not date_range_known:
            notes.append("You indicated a trip-style need, but execution gets safer once you know the exact start and end dates.")
        return WorkflowWizardResult(
            recommended_workflow=workflow,
            matched_problem=None,
            confidence=confidence,
            reason=reason,
            notes=notes,
            command_suggestions=_build_command_suggestions(workflow.name),
        )

    if source_count > 1 or has_duplicates:
        workflow = get_workflow_definition("cleanup")
        if workflow is None:
            raise RuntimeError("Catalog inconsistency: missing cleanup workflow")
        reason = "Multiple sources or duplicate concerns make the cleanup workflow the safest first overview."
        if source_count > 1:
            notes.append("The cleanup workflow is especially useful when several source folders need one combined plan.")
        if has_duplicates:
            notes.append("Cleanup includes exact duplicate analysis before organize or rename decisions.")
        return WorkflowWizardResult(
            recommended_workflow=workflow,
            matched_problem=None,
            confidence="high",
            reason=reason,
            notes=notes,
            command_suggestions=_build_command_suggestions(workflow.name),
        )

    if wants_rename and not wants_organization:
        workflow = get_workflow_definition("rename")
        if workflow is None:
            raise RuntimeError("Catalog inconsistency: missing rename workflow")
        return WorkflowWizardResult(
            recommended_workflow=workflow,
            matched_problem=None,
            confidence="medium",
            reason="Template-based file naming looks like the main problem you want to solve first.",
            notes=["Run rename as dry-run first, then apply only after reviewing collisions and skipped files."],
            command_suggestions=_build_command_suggestions(workflow.name),
        )

    workflow = get_workflow_definition("organize")
    if workflow is None:
        raise RuntimeError("Catalog inconsistency: missing organize workflow")
    reason = "Folder structure appears to be the main issue, so organize is the most direct starting point."
    if wants_organization and wants_rename:
        notes.append("Start with organize first, then standardize names afterwards to keep each step easier to review.")
    return WorkflowWizardResult(
        recommended_workflow=workflow,
        matched_problem=None,
        confidence="medium",
        reason=reason,
        notes=notes,
        command_suggestions=_build_command_suggestions(workflow.name),
    )
