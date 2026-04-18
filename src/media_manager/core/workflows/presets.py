from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .catalog import get_workflow_definition


PROFILE_SCHEMA_VERSION = 1


@dataclass(slots=True, frozen=True)
class WorkflowPreset:
    name: str
    title: str
    summary: str
    workflow: str
    required_values: tuple[str, ...]
    default_values: dict[str, object] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True, frozen=True)
class WorkflowProfile:
    profile_name: str
    preset_name: str
    values: dict[str, object]


WORKFLOW_PRESETS: tuple[WorkflowPreset, ...] = (
    WorkflowPreset(
        name="cleanup-family-library",
        title="Cleanup family library",
        summary=(
            "Best starting point for several messy photo/video sources where you want a safe guided overview "
            "before organizing and renaming anything."
        ),
        workflow="cleanup",
        required_values=("source", "target"),
        default_values={
            "duplicate_policy": "first",
            "duplicate_mode": "copy",
            "organize_pattern": "{year}/{year_month_day}/{source_name}",
            "rename_template": "{date:%Y-%m-%d_%H-%M-%S}_{source_name}_{stem}",
        },
        notes=(
            "Start with dry-run output and review duplicates first.",
            "Apply organize or rename in separate steps after reviewing the plan.",
        ),
    ),
    WorkflowPreset(
        name="trip-hardlink-collection",
        title="Trip hardlink collection",
        summary=(
            "Build a trip/event collection from one or more sources without copying bytes twice when possible."
        ),
        workflow="trip",
        required_values=("source", "target", "label", "start", "end"),
        default_values={
            "mode": "link",
        },
        notes=(
            "Great when you know the date range already.",
            "Use copy mode instead if the target must live on a different filesystem.",
        ),
    ),
    WorkflowPreset(
        name="duplicate-review-safe",
        title="Duplicate review safe start",
        summary=(
            "Start duplicate work conservatively with an auto-selected keep candidate and visible planning output."
        ),
        workflow="duplicates",
        required_values=("source",),
        default_values={
            "policy": "first",
            "mode": "delete",
            "show_plan": True,
        },
        notes=(
            "Still review the proposed keep candidate before applying delete mode.",
        ),
    ),
    WorkflowPreset(
        name="organize-date-library",
        title="Organize by date library",
        summary=(
            "Sort media into a date-oriented target library using the rebuilt organizer and date resolver."
        ),
        workflow="organize",
        required_values=("source", "target"),
        default_values={
            "pattern": "{year}/{year_month_day}/{source_name}",
        },
        notes=(
            "Run dry-run first and only then apply.",
        ),
    ),
    WorkflowPreset(
        name="rename-capture-standard",
        title="Rename to capture standard",
        summary=(
            "Standardize filenames with a date-first template based on resolved capture times."
        ),
        workflow="rename",
        required_values=("source",),
        default_values={
            "template": "{date:%Y-%m-%d_%H-%M-%S}_{stem}",
        },
        notes=(
            "Use after or before organize depending on your preferred library flow.",
        ),
    ),
)


def list_workflow_presets() -> list[WorkflowPreset]:
    return list(WORKFLOW_PRESETS)


def get_workflow_preset(name: str) -> WorkflowPreset | None:
    normalized = name.strip().lower()
    for item in WORKFLOW_PRESETS:
        if item.name == normalized:
            return item
    return None


def _normalize_profile_values(values: dict[str, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, value in values.items():
        if isinstance(value, list):
            normalized[str(key)] = [str(item) for item in value]
        elif isinstance(value, (str, int, float, bool)) or value is None:
            normalized[str(key)] = value
        else:
            normalized[str(key)] = str(value)
    return normalized


def _is_missing_required_value(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False


def load_workflow_profile(path: str | Path) -> WorkflowProfile:
    file_path = Path(path)
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Workflow profile must be a JSON object.")
    if int(payload.get("schema_version", 0)) != PROFILE_SCHEMA_VERSION:
        raise ValueError("Workflow profile schema_version must be 1.")

    profile_name = str(payload.get("profile_name", "")).strip() or file_path.stem
    preset_name = str(payload.get("preset", "")).strip()
    if not preset_name:
        raise ValueError("Workflow profile must define a preset name.")

    raw_values = payload.get("values", {})
    if not isinstance(raw_values, dict):
        raise ValueError("Workflow profile values must be a JSON object.")

    return WorkflowProfile(
        profile_name=profile_name,
        preset_name=preset_name,
        values=_normalize_profile_values(raw_values),
    )


def _quote_if_needed(value: str) -> str:
    return f'"{value}"' if any(ch.isspace() for ch in value) else value


def _extend_source_args(parts: list[str], values: dict[str, object]) -> None:
    sources = values.get("source")
    if isinstance(sources, list):
        source_values = [str(item) for item in sources]
    elif sources is None:
        source_values = []
    else:
        source_values = [str(sources)]

    for item in source_values:
        parts.extend(["--source", _quote_if_needed(item)])


def _build_command_parts_for_preset(preset: WorkflowPreset, values: dict[str, object]) -> list[str]:
    workflow = preset.workflow
    parts = ["media-manager", "workflow", "run", workflow]
    _extend_source_args(parts, values)

    def add_arg(flag: str, key: str) -> None:
        value = values.get(key)
        if _is_missing_required_value(value):
            return
        parts.extend([flag, _quote_if_needed(str(value))])

    if workflow == "cleanup":
        add_arg("--target", "target")
        add_arg("--organize-pattern", "organize_pattern")
        add_arg("--rename-template", "rename_template")
        add_arg("--duplicate-policy", "duplicate_policy")
        add_arg("--duplicate-mode", "duplicate_mode")
    elif workflow == "trip":
        add_arg("--target", "target")
        add_arg("--label", "label")
        add_arg("--start", "start")
        add_arg("--end", "end")
        mode = str(values.get("mode", "link"))
        parts.append("--copy" if mode == "copy" else "--link")
    elif workflow == "duplicates":
        add_arg("--policy", "policy")
        add_arg("--mode", "mode")
        if bool(values.get("show_plan", False)):
            parts.append("--show-plan")
    elif workflow == "organize":
        add_arg("--target", "target")
        add_arg("--pattern", "pattern")
    elif workflow == "rename":
        add_arg("--template", "template")

    return parts


def render_workflow_preset_command(
    preset_name: str,
    *,
    overrides: dict[str, object] | None = None,
) -> str:
    preset = get_workflow_preset(preset_name)
    if preset is None:
        raise ValueError(f"Unknown workflow preset: {preset_name}")

    workflow = get_workflow_definition(preset.workflow)
    if workflow is None:
        raise ValueError(f"Preset points to unknown workflow: {preset.workflow}")

    values = dict(preset.default_values)
    if overrides:
        values.update(_normalize_profile_values(overrides))

    missing = [
        key
        for key in preset.required_values
        if key not in values or _is_missing_required_value(values[key])
    ]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Workflow preset '{preset.name}' is missing required values: {missing_text}")

    return " ".join(_build_command_parts_for_preset(preset, values))


def render_workflow_profile_command(profile: WorkflowProfile) -> str:
    return render_workflow_preset_command(profile.preset_name, overrides=profile.values)


def build_workflow_profile_payload(
    *,
    profile_name: str,
    preset_name: str,
    values: dict[str, object],
) -> dict[str, object]:
    normalized_values = _normalize_profile_values(values)
    return {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "profile_name": profile_name.strip() or "workflow-profile",
        "preset": preset_name,
        "values": normalized_values,
    }


def save_workflow_profile(
    path: str | Path,
    *,
    profile_name: str,
    preset_name: str,
    values: dict[str, object],
    overwrite: bool = False,
) -> WorkflowProfile:
    payload = build_workflow_profile_payload(
        profile_name=profile_name,
        preset_name=preset_name,
        values=values,
    )

    profile = WorkflowProfile(
        profile_name=str(payload["profile_name"]),
        preset_name=str(payload["preset"]),
        values=dict(payload["values"]),
    )

    render_workflow_profile_command(profile)

    file_path = Path(path)
    if file_path.exists() and not overwrite:
        raise FileExistsError(f"Workflow profile already exists: {file_path}")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return profile
