from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .catalog import get_workflow_definition, get_workflow_problem, list_workflow_problems, list_workflows


@dataclass(slots=True, frozen=True)
class GuiShellWorkflowCard:
    name: str
    title: str
    summary: str
    best_for: str
    example_command: str


@dataclass(slots=True, frozen=True)
class GuiShellProblemCard:
    name: str
    title: str
    summary: str
    recommended_workflow: str
    next_step: str
    recommended_command: str


@dataclass(slots=True)
class GuiShellModel:
    workflows: list[GuiShellWorkflowCard] = field(default_factory=list)
    problems: list[GuiShellProblemCard] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "workflows": [asdict(item) for item in self.workflows],
            "problems": [asdict(item) for item in self.problems],
        }


def build_gui_shell_model() -> GuiShellModel:
    workflows = [
        GuiShellWorkflowCard(
            name=item.name,
            title=item.title,
            summary=item.summary,
            best_for=item.best_for,
            example_command=item.example_command,
        )
        for item in list_workflows()
    ]

    problems: list[GuiShellProblemCard] = []
    for problem in list_workflow_problems():
        workflow = get_workflow_definition(problem.recommended_workflow)
        recommended_command = "" if workflow is None else workflow.example_command
        problems.append(
            GuiShellProblemCard(
                name=problem.name,
                title=problem.title,
                summary=problem.summary,
                recommended_workflow=problem.recommended_workflow,
                next_step=problem.next_step,
                recommended_command=recommended_command,
            )
        )

    return GuiShellModel(workflows=workflows, problems=problems)


def build_shell_command_preview_for_workflow(name: str) -> str:
    workflow = get_workflow_definition(name)
    if workflow is None:
        raise ValueError(f"Unknown workflow: {name}")
    return workflow.example_command


def build_shell_command_preview_for_problem(name: str) -> str:
    problem = get_workflow_problem(name)
    if problem is None:
        raise ValueError(f"Unknown workflow problem: {name}")
    workflow = get_workflow_definition(problem.recommended_workflow)
    if workflow is None:
        raise ValueError(f"Workflow problem points to unknown workflow: {problem.recommended_workflow}")
    return workflow.example_command
