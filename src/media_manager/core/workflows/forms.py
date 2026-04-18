from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from .catalog import get_workflow_definition, list_workflows
from .presets import (
    WorkflowProfile,
    WorkflowPreset,
    get_workflow_preset,
    load_workflow_profile,
    render_workflow_profile_command,
    render_workflow_preset_command,
)


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


@dataclass(slots=True, frozen=True)
class BoundWorkflowFormField:
    name: str
    label: str
    kind: str
    required: bool
    multiple: bool
    choices: tuple[str, ...]
    help_text: str
    default: str | None
    value: object | None
    value_source: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "label": self.label,
            "kind": self.kind,
            "required": self.required,
            "multiple": self.multiple,
            "choices": list(self.choices),
            "help_text": self.help_text,
            "default": self.default,
            "value": self.value,
            "value_source": self.value_source,
        }


@dataclass(slots=True, frozen=True)
class BoundWorkflowFormModel:
    workflow_name: str
    title: str
    summary: str
    preset_name: str | None
    profile_name: str | None
    missing_required_fields: tuple[str, ...] = ()
    command_preview: str | None = None
    fields: tuple[BoundWorkflowFormField, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "workflow_name": self.workflow_name,
            "title": self.title,
            "summary": self.summary,
            "preset_name": self.preset_name,
            "profile_name": self.profile_name,
            "missing_required_fields": list(self.missing_required_fields),
            "command_preview": self.command_preview,
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


def _is_missing_value(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False


def _bind_form_model(
    base_model: WorkflowFormModel,
    *,
    preset_name: str | None,
    profile_name: str | None,
    values: dict[str, object],
    command_preview: str | None,
) -> BoundWorkflowFormModel:
    bound_fields: list[BoundWorkflowFormField] = []
    missing_required_fields: list[str] = []

    for field_model in base_model.fields:
        if field_model.name in values:
            value = values[field_model.name]
            value_source = "binding"
        else:
            value = field_model.default
            value_source = "form-default" if field_model.default is not None else "empty"

        if field_model.required and _is_missing_value(value):
            missing_required_fields.append(field_model.name)

        bound_fields.append(
            BoundWorkflowFormField(
                name=field_model.name,
                label=field_model.label,
                kind=field_model.kind,
                required=field_model.required,
                multiple=field_model.multiple,
                choices=field_model.choices,
                help_text=field_model.help_text,
                default=field_model.default,
                value=value,
                value_source=value_source,
            )
        )

    return BoundWorkflowFormModel(
        workflow_name=base_model.workflow_name,
        title=base_model.title,
        summary=base_model.summary,
        preset_name=preset_name,
        profile_name=profile_name,
        missing_required_fields=tuple(missing_required_fields),
        command_preview=command_preview,
        fields=tuple(bound_fields),
    )


def build_preset_bound_workflow_form_model(preset_name: str) -> BoundWorkflowFormModel:
    preset = get_workflow_preset(preset_name)
    if preset is None:
        raise ValueError(f"Unknown workflow preset: {preset_name}")

    base_model = build_workflow_form_model(preset.workflow)
    values = dict(preset.default_values)
    try:
        command_preview = render_workflow_preset_command(preset.name)
    except Exception:
        command_preview = None

    return _bind_form_model(
        base_model,
        preset_name=preset.name,
        profile_name=None,
        values=values,
        command_preview=command_preview,
    )


def build_profile_bound_workflow_form_model(profile: WorkflowProfile | str | Path) -> BoundWorkflowFormModel:
    if isinstance(profile, (str, Path)):
        loaded = load_workflow_profile(profile)
    else:
        loaded = profile

    preset = get_workflow_preset(loaded.preset_name)
    if preset is None:
        raise ValueError(f"Unknown workflow preset: {loaded.preset_name}")

    base_model = build_workflow_form_model(preset.workflow)
    values = dict(preset.default_values)
    values.update(dict(loaded.values))
    try:
        command_preview = render_workflow_profile_command(loaded)
    except Exception:
        command_preview = None

    return _bind_form_model(
        base_model,
        preset_name=preset.name,
        profile_name=loaded.profile_name,
        values=values,
        command_preview=command_preview,
    )
