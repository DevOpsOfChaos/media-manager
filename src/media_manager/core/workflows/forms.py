from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from .catalog import get_workflow_definition, list_workflows
from .presets import (
    WorkflowProfile,
    WorkflowPreset,
    get_workflow_preset,
    load_workflow_profile,
    render_workflow_preset_command,
    validate_workflow_profile,
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
    valid: bool
    missing_required_fields: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()
    command_preview: str | None = None
    binding_summary: dict[str, object] = field(default_factory=dict)
    fields: tuple[BoundWorkflowFormField, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "workflow_name": self.workflow_name,
            "title": self.title,
            "summary": self.summary,
            "preset_name": self.preset_name,
            "profile_name": self.profile_name,
            "valid": self.valid,
            "missing_required_fields": list(self.missing_required_fields),
            "problems": list(self.problems),
            "command_preview": self.command_preview,
            "binding_summary": dict(self.binding_summary),
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
        _field("include_hidden", "Include hidden", "bool", default="false"),
        _field("json_output", "JSON output", "bool", default="false"),
        _field("run_log", "Run log path", "path"),
        _field("history_dir", "History directory", "path"),
    ),
    "trip": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("target", "Trip target root", "path", required=True),
        _field("label", "Trip label", "text", required=True, help_text="For example Italy_2025."),
        _field("start", "Start date", "date", required=True),
        _field("end", "End date", "date", required=True),
        _field("mode", "Collection mode", "choice", default="link", choices=("link", "copy")),
        _field("non_recursive", "Non-recursive", "bool", default="false"),
        _field("include_hidden", "Include hidden", "bool", default="false"),
        _field("show_files", "Show files", "bool", default="false"),
        _field("json_output", "JSON output", "bool", default="false"),
        _field("run_log", "Run log path", "path"),
        _field("history_dir", "History directory", "path"),
        _field("journal", "Execution journal path", "path"),
        _field("apply", "Apply", "bool", default="false"),
    ),
    "duplicates": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("policy", "Keep policy", "choice", default="first", choices=("first", "newest", "oldest")),
        _field("mode", "Execution mode", "choice", default="delete", choices=("copy", "move", "delete")),
        _field("show_plan", "Show plan", "bool", default="true"),
        _field("similar_images", "Similar images", "bool", default="false"),
        _field("show_similar_groups", "Show similar groups", "bool", default="false"),
        _field("show_similar_review", "Show similar review", "bool", default="false"),
        _field("similar_threshold", "Similar threshold", "number", default="6"),
        _field("run_log", "Run log path", "path"),
        _field("history_dir", "History directory", "path"),
        _field("journal", "Execution journal path", "path"),
        _field("apply", "Apply", "bool", default="false"),
        _field("yes", "Confirm apply", "bool", default="false"),
    ),
    "organize": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("target", "Target root", "path", required=True),
        _field("pattern", "Directory pattern", "text", default="{year}/{year_month_day}/{source_name}"),
        _field("mode", "Operation mode", "choice", default="copy", choices=("copy", "move")),
        _field("non_recursive", "Non-recursive", "bool", default="false"),
        _field("include_hidden", "Include hidden", "bool", default="false"),
        _field("show_files", "Show files", "bool", default="false"),
        _field("json_output", "JSON output", "bool", default="false"),
        _field("run_log", "Run log path", "path"),
        _field("history_dir", "History directory", "path"),
        _field("journal", "Execution journal path", "path"),
        _field("apply", "Apply", "bool", default="false"),
    ),
    "rename": (
        _field("source", "Source folders", "path", required=True, multiple=True),
        _field("template", "Rename template", "text", default="{date:%Y-%m-%d_%H-%M-%S}_{stem}"),
        _field("non_recursive", "Non-recursive", "bool", default="false"),
        _field("include_hidden", "Include hidden", "bool", default="false"),
        _field("show_files", "Show files", "bool", default="false"),
        _field("json_output", "JSON output", "bool", default="false"),
        _field("run_log", "Run log path", "path"),
        _field("history_dir", "History directory", "path"),
        _field("journal", "Execution journal path", "path"),
        _field("apply", "Apply", "bool", default="false"),
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




def _build_problem_aliases(problems: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    aliases: list[str] = []
    for item in problems:
        if item == "Similar review requires similar_images.":
            aliases.append("show_similar_review requires similar_images")
        elif item == "Duplicate apply mode requires yes confirmation.":
            aliases.append("duplicates apply requires yes")
        elif item == "Journal output requires apply mode.":
            aliases.append("journal requires apply")
    return tuple(aliases)

def _build_binding_summary(fields: list[BoundWorkflowFormField], missing_required_fields: list[str]) -> dict[str, object]:
    value_source_summary: dict[str, int] = {}
    filled_field_count = 0
    for item in fields:
        value_source_summary[item.value_source] = value_source_summary.get(item.value_source, 0) + 1
        if not _is_missing_value(item.value):
            filled_field_count += 1
    return {
        "field_count": len(fields),
        "filled_field_count": filled_field_count,
        "missing_required_count": len(missing_required_fields),
        "value_source_summary": dict(sorted(value_source_summary.items())),
    }


def _bind_form_model(
    base_model: WorkflowFormModel,
    *,
    preset_name: str | None,
    profile_name: str | None,
    values: dict[str, object],
    value_sources: dict[str, str],
    command_preview: str | None,
    explicit_problems: tuple[str, ...] = (),
    explicit_missing_required_fields: tuple[str, ...] | None = None,
) -> BoundWorkflowFormModel:
    bound_fields: list[BoundWorkflowFormField] = []
    missing_required_fields: list[str] = []

    for field_model in base_model.fields:
        if field_model.name in values:
            value = values[field_model.name]
            value_source = value_sources.get(field_model.name, "binding")
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

    if explicit_missing_required_fields is not None:
        merged_missing = list(dict.fromkeys([*missing_required_fields, *explicit_missing_required_fields]))
    else:
        merged_missing = missing_required_fields

    problems: list[str] = list(dict.fromkeys([*explicit_problems, *_build_problem_aliases(explicit_problems)]))
    if merged_missing and not any("Missing required" in item for item in problems):
        problems.insert(0, "Missing required fields: " + ", ".join(merged_missing))
    if not problems and command_preview is None:
        problems.append("Command preview could not be rendered from the current binding.")

    binding_summary = _build_binding_summary(bound_fields, merged_missing)
    return BoundWorkflowFormModel(
        workflow_name=base_model.workflow_name,
        title=base_model.title,
        summary=base_model.summary,
        preset_name=preset_name,
        profile_name=profile_name,
        valid=len(problems) == 0,
        missing_required_fields=tuple(merged_missing),
        problems=tuple(problems),
        command_preview=command_preview,
        binding_summary=binding_summary,
        fields=tuple(bound_fields),
    )


def build_preset_bound_workflow_form_model(preset_name: str) -> BoundWorkflowFormModel:
    preset = get_workflow_preset(preset_name)
    if preset is None:
        raise ValueError(f"Unknown workflow preset: {preset_name}")

    base_model = build_workflow_form_model(preset.workflow)
    values = dict(preset.default_values)
    value_sources = {key: "preset-default" for key in values}
    try:
        command_preview = render_workflow_preset_command(preset.name)
    except Exception:
        command_preview = None

    return _bind_form_model(
        base_model,
        preset_name=preset.name,
        profile_name=None,
        values=values,
        value_sources=value_sources,
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
    value_sources = {key: "preset-default" for key in preset.default_values}
    value_sources.update({key: "profile-value" for key in loaded.values})
    validation = validate_workflow_profile(loaded)

    return _bind_form_model(
        base_model,
        preset_name=preset.name,
        profile_name=loaded.profile_name,
        values=values,
        value_sources=value_sources,
        command_preview=validation.command_preview,
        explicit_problems=validation.problems,
        explicit_missing_required_fields=validation.missing_values,
    )
