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


@dataclass(slots=True, frozen=True)
class WorkflowProfileValidation:
    profile_name: str
    preset_name: str
    workflow_name: str | None
    valid: bool
    missing_values: tuple[str, ...]
    command_argv: tuple[str, ...]
    command_preview: str | None
    problems: tuple[str, ...]


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
        name="trip-copy-review",
        title="Trip copy review",
        summary=(
            "Review a trip collection in copy mode with file-level output and JSON payloads before applying anything."
        ),
        workflow="trip",
        required_values=("source", "target", "label", "start", "end"),
        default_values={
            "mode": "copy",
            "show_files": True,
            "json_output": True,
        },
        notes=(
            "Useful when the collection target should be a true copy rather than hard links.",
            "The rendered command stays in dry-run mode until you explicitly add apply in a profile JSON.",
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
        name="duplicates-similar-review",
        title="Duplicates plus similar-image review",
        summary=(
            "Combine exact-duplicate planning with similar-image review helpers so you can inspect both in one run."
        ),
        workflow="duplicates",
        required_values=("source",),
        default_values={
            "policy": "first",
            "mode": "delete",
            "show_plan": True,
            "show_decisions": True,
            "similar_images": True,
            "show_similar_review": True,
            "similar_policy": "first",
        },
        notes=(
            "Designed for review mode, not for immediate deletion.",
            "Add apply and yes explicitly in a saved profile only after manual review.",
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
        name="organize-review-json",
        title="Organize review JSON",
        summary=(
            "Render an organizer dry run with machine-readable JSON plus file-level detail for easier inspection."
        ),
        workflow="organize",
        required_values=("source", "target"),
        default_values={
            "pattern": "{year}/{year_month_day}/{source_name}",
            "show_files": True,
            "json_output": True,
        },
        notes=(
            "Useful when you want to inspect the exact plan before any apply run.",
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
    WorkflowPreset(
        name="rename-review-json",
        title="Rename review JSON",
        summary=(
            "Render a rename dry run with file-level output and JSON so the plan can be reviewed or logged easily."
        ),
        workflow="rename",
        required_values=("source",),
        default_values={
            "template": "{date:%Y-%m-%d_%H-%M-%S}_{stem}",
            "show_files": True,
            "json_output": True,
        },
        notes=(
            "Helpful for checking naming decisions before any apply run.",
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


def _render_command_parts(parts: list[str]) -> str:
    return " ".join(_quote_if_needed(part) for part in parts)


def _extend_source_args(parts: list[str], values: dict[str, object]) -> None:
    sources = values.get("source")
    if isinstance(sources, list):
        source_values = [str(item) for item in sources]
    elif sources is None:
        source_values = []
    else:
        source_values = [str(sources)]

    for item in source_values:
        parts.extend(["--source", item])


def _resolve_preset_values(preset: WorkflowPreset, overrides: dict[str, object] | None) -> dict[str, object]:
    values = dict(preset.default_values)
    if overrides:
        values.update(_normalize_profile_values(overrides))
    return values


def _append_optional_arg(parts: list[str], values: dict[str, object], flag: str, key: str) -> None:
    value = values.get(key)
    if _is_missing_required_value(value):
        return
    parts.extend([flag, str(value)])


def _append_optional_flag(parts: list[str], values: dict[str, object], key: str, flag: str) -> None:
    if bool(values.get(key, False)):
        parts.append(flag)


def _append_common_runtime_flags(
    parts: list[str],
    values: dict[str, object],
    *,
    include_json_output: bool,
    include_apply: bool,
    include_journal: bool,
    include_yes: bool = False,
) -> None:
    _append_optional_flag(parts, values, "non_recursive", "--non-recursive")
    _append_optional_flag(parts, values, "include_hidden", "--include-hidden")
    _append_optional_flag(parts, values, "show_files", "--show-files")
    if include_json_output:
        _append_optional_flag(parts, values, "json_output", "--json")
    if include_apply:
        _append_optional_flag(parts, values, "apply", "--apply")
    if include_yes:
        _append_optional_flag(parts, values, "yes", "--yes")
    _append_optional_arg(parts, values, "--run-log", "run_log")
    _append_optional_arg(parts, values, "--history-dir", "history_dir")
    if include_journal:
        _append_optional_arg(parts, values, "--journal", "journal")
    _append_optional_arg(parts, values, "--exiftool-path", "exiftool_path")


def _build_command_parts_for_preset(preset: WorkflowPreset, values: dict[str, object]) -> list[str]:
    workflow = preset.workflow
    parts = ["media-manager", "workflow", "run", workflow]
    _extend_source_args(parts, values)

    if workflow == "cleanup":
        _append_optional_arg(parts, values, "--target", "target")
        _append_optional_arg(parts, values, "--organize-pattern", "organize_pattern")
        _append_optional_arg(parts, values, "--rename-template", "rename_template")
        _append_optional_arg(parts, values, "--duplicate-policy", "duplicate_policy")
        _append_optional_arg(parts, values, "--duplicate-mode", "duplicate_mode")
        return parts

    if workflow == "trip":
        _append_optional_arg(parts, values, "--target", "target")
        _append_optional_arg(parts, values, "--label", "label")
        _append_optional_arg(parts, values, "--start", "start")
        _append_optional_arg(parts, values, "--end", "end")
        mode = str(values.get("mode", "link"))
        parts.append("--copy" if mode == "copy" else "--link")
        _append_common_runtime_flags(parts, values, include_json_output=True, include_apply=True, include_journal=True)
        return parts

    if workflow == "duplicates":
        _append_optional_arg(parts, values, "--policy", "policy")
        _append_optional_arg(parts, values, "--mode", "mode")
        _append_optional_flag(parts, values, "show_groups", "--show-groups")
        _append_optional_flag(parts, values, "show_decisions", "--show-decisions")
        _append_optional_flag(parts, values, "show_unresolved", "--show-unresolved")
        _append_optional_flag(parts, values, "show_plan", "--show-plan")
        _append_optional_flag(parts, values, "similar_images", "--similar-images")
        _append_optional_flag(parts, values, "show_similar_groups", "--show-similar-groups")
        _append_optional_flag(parts, values, "show_similar_review", "--show-similar-review")
        _append_optional_arg(parts, values, "--similar-threshold", "similar_threshold")
        _append_optional_arg(parts, values, "--similar-policy", "similar_policy")
        _append_optional_arg(parts, values, "--load-session", "load_session")
        _append_optional_arg(parts, values, "--save-session", "save_session")
        _append_optional_arg(parts, values, "--json-report", "json_report")
        _append_common_runtime_flags(parts, values, include_json_output=False, include_apply=True, include_journal=True, include_yes=True)
        return parts

    if workflow == "organize":
        _append_optional_arg(parts, values, "--target", "target")
        _append_optional_arg(parts, values, "--pattern", "pattern")
        _append_common_runtime_flags(parts, values, include_json_output=True, include_apply=True, include_journal=True)
        return parts

    if workflow == "rename":
        _append_optional_arg(parts, values, "--template", "template")
        _append_common_runtime_flags(parts, values, include_json_output=True, include_apply=True, include_journal=True)
        return parts

    return parts


def build_workflow_preset_argv(
    preset_name: str,
    *,
    overrides: dict[str, object] | None = None,
) -> list[str]:
    preset = get_workflow_preset(preset_name)
    if preset is None:
        raise ValueError(f"Unknown workflow preset: {preset_name}")

    workflow = get_workflow_definition(preset.workflow)
    if workflow is None:
        raise ValueError(f"Preset points to unknown workflow: {preset.workflow}")

    values = _resolve_preset_values(preset, overrides)
    missing = [
        key
        for key in preset.required_values
        if key not in values or _is_missing_required_value(values[key])
    ]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Workflow preset '{preset.name}' is missing required values: {missing_text}")

    return _build_command_parts_for_preset(preset, values)


def render_workflow_preset_command(
    preset_name: str,
    *,
    overrides: dict[str, object] | None = None,
) -> str:
    return _render_command_parts(build_workflow_preset_argv(preset_name, overrides=overrides))


def build_workflow_profile_argv(profile: WorkflowProfile) -> list[str]:
    return build_workflow_preset_argv(profile.preset_name, overrides=profile.values)


def render_workflow_profile_command(profile: WorkflowProfile) -> str:
    return _render_command_parts(build_workflow_profile_argv(profile))


def _coerce_optional_int(value: object) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def validate_workflow_profile(profile: WorkflowProfile) -> WorkflowProfileValidation:
    preset = get_workflow_preset(profile.preset_name)
    if preset is None:
        return WorkflowProfileValidation(
            profile_name=profile.profile_name,
            preset_name=profile.preset_name,
            workflow_name=None,
            valid=False,
            missing_values=(),
            command_argv=(),
            command_preview=None,
            problems=(f"Unknown workflow preset: {profile.preset_name}",),
        )

    values = _resolve_preset_values(preset, profile.values)
    missing = tuple(
        key
        for key in preset.required_values
        if key not in values or _is_missing_required_value(values[key])
    )
    problems: list[str] = []
    if missing:
        problems.append(f"Missing required values: {', '.join(missing)}")

    workflow = get_workflow_definition(preset.workflow)
    if workflow is None:
        problems.append(f"Preset points to unknown workflow: {preset.workflow}")

    apply_requested = bool(values.get("apply", False))
    journal_value = values.get("journal")
    if preset.workflow in {"organize", "rename", "trip", "duplicates"} and not _is_missing_required_value(journal_value) and not apply_requested:
        problems.append("Journal output requires apply mode.")

    if preset.workflow == "duplicates":
        if apply_requested and not bool(values.get("yes", False)):
            problems.append("Duplicate apply mode requires yes confirmation.")
        if bool(values.get("show_similar_review", False)) and not bool(values.get("similar_images", False)):
            problems.append("Similar review requires similar_images.")
        similar_threshold = _coerce_optional_int(values.get("similar_threshold"))
        if similar_threshold is not None and similar_threshold < 0:
            problems.append("Similar threshold must be zero or greater.")

    command_argv: tuple[str, ...] = ()
    command_preview: str | None = None
    if not problems:
        parts = _build_command_parts_for_preset(preset, values)
        command_argv = tuple(parts)
        command_preview = _render_command_parts(parts)

    return WorkflowProfileValidation(
        profile_name=profile.profile_name,
        preset_name=profile.preset_name,
        workflow_name=preset.workflow,
        valid=len(problems) == 0,
        missing_values=missing,
        command_argv=command_argv,
        command_preview=command_preview,
        problems=tuple(problems),
    )


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

    validation = validate_workflow_profile(profile)
    if not validation.valid:
        raise ValueError("; ".join(validation.problems))

    file_path = Path(path)
    if file_path.exists() and not overwrite:
        raise FileExistsError(f"Workflow profile already exists: {file_path}")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return profile
