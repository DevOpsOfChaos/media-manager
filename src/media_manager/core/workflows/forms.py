from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .catalog import get_workflow_definition, list_workflows


@dataclass(slots=True, frozen=True)
class WorkflowFormField:
    name: str
    label: str
    kind: str
    required: bool = False
    multiple: bool = False
    default: str | None = None
    choices: tuple[str, ...] = ()
    help_text: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class WorkflowFormModel:
    workflow_name: str
    title: str
    summary: str
    fields: tuple[WorkflowFormField, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "workflow_name": self.workflow_name,
            "title": self.title,
            "summary": self.summary,
            "fields": [item.to_dict() for item in self.fields],
        }


def _field(
    name: str,
    label: str,
    kind: str,
    *,
    required: bool = False,
    multiple: bool = False,
    default: str | None = None,
    choices: tuple[str, ...] = (),
    help_text: str = "",
) -> WorkflowFormField:
    return WorkflowFormField(
        name=name,
        label=label,
        kind=kind,
        required=required,
        multiple=multiple,
        default=default,
        choices=choices,
        help_text=help_text,
    )


_FORM_FIELDS: dict[str, tuple[WorkflowFormField, ...]] = {
    "cleanup": (
        _field("source", "Source folders", "path", required=True, multiple=True, help_text="Repeatable source folders that should be scanned together."),
        _field("target", "Target root", "path", required=True, help_text="Root directory for organize planning and execution."),
        _field("duplicate_policy", "Duplicate keep policy", "choice", default="first", choices=("first", "newest", "oldest")),
        _field("duplicate_mode", "Duplicate mode", "choice", default="copy", choices=("copy", "move", "delete")),
        _field("organize_pattern", "Organize pattern", "text", default="{year}/{year_month_day}/{source_name}"),
        _field("rename_template", "Rename template", "text", default="{date:%Y-%m-%d_%H-%M-%S}_{source_name}_{stem}"),
    ),
    "trip": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("target", "Trip target root", "path", required=True),
        _field("label", "Trip label", "text", required=True, help_text="For example Italy_2025."),
        _field("start", "Start date", "date", required=True),
        _field("end", "End date", "date", required=True),
        _field("mode", "Collection mode", "choice", default="link", choices=("link", "copy")),
    ),
    "duplicates": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("policy", "Keep policy", "choice", default="first", choices=("first", "newest", "oldest")),
        _field("mode", "Execution mode", "choice", default="delete", choices=("copy", "move", "delete")),
        _field("show_plan", "Show plan", "bool", default="true"),
    ),
    "organize": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("target", "Target root", "path", required=True),
        _field("pattern", "Directory pattern", "text", default="{year}/{year_month_day}/{source_name}"),
        _field("mode", "Operation mode", "choice", default="copy", choices=("copy", "move")),
    ),
    "rename": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("template", "Rename template", "text", default="{date:%Y-%m-%d_%H-%M-%S}_{stem}"),
    ),
}


def build_workflow_form_model(workflow_name: str) -> WorkflowFormModel:
    workflow = get_workflow_definition(workflow_name)
    if workflow is None:
        raise ValueError(f"Unknown workflow: {workflow_name}")

    fields = _FORM_FIELDS.get(workflow.name)
    if fields is None:
        raise ValueError(f"No workflow form model defined for: {workflow.name}")

    return WorkflowFormModel(
        workflow_name=workflow.name,
        title=workflow.title,
        summary=workflow.summary,
        fields=fields,
    )


def list_workflow_form_models() -> list[WorkflowFormModel]:
    models: list[WorkflowFormModel] = []
    for workflow in list_workflows():
        if workflow.name not in _FORM_FIELDS:
            continue
        models.append(build_workflow_form_model(workflow.name))
    return models
