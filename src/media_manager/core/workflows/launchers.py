from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .forms import build_preset_bound_workflow_form_model, build_profile_bound_workflow_form_model
from .presets import get_workflow_preset, list_workflow_presets


@dataclass(slots=True, frozen=True)
class PresetLauncherCard:
    name: str
    title: str
    workflow_name: str
    ready_to_run: bool
    missing_required_fields: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "title": self.title,
            "workflow_name": self.workflow_name,
            "ready_to_run": self.ready_to_run,
            "missing_required_fields": list(self.missing_required_fields),
        }


@dataclass(slots=True, frozen=True)
class ProfileLauncherCard:
    path: str
    profile_name: str
    preset_name: str
    workflow_name: str | None
    valid: bool
    command_preview: str | None
    problems: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "profile_name": self.profile_name,
            "preset_name": self.preset_name,
            "workflow_name": self.workflow_name,
            "valid": self.valid,
            "command_preview": self.command_preview,
            "problems": list(self.problems),
        }


@dataclass(slots=True)
class WorkflowLauncherModel:
    presets: list[PresetLauncherCard] = field(default_factory=list)
    profiles: list[ProfileLauncherCard] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "presets": [item.to_dict() for item in self.presets],
            "profiles": [item.to_dict() for item in self.profiles],
        }


def build_workflow_launcher_model(profiles_dir: str | Path | None = None) -> WorkflowLauncherModel:
    model = WorkflowLauncherModel()

    for preset in list_workflow_presets():
        bound = build_preset_bound_workflow_form_model(preset.name)
        model.presets.append(
            PresetLauncherCard(
                name=preset.name,
                title=preset.title,
                workflow_name=bound.workflow_name,
                ready_to_run=len(bound.missing_required_fields) == 0,
                missing_required_fields=bound.missing_required_fields,
            )
        )

    if profiles_dir is None:
        return model

    base_dir = Path(profiles_dir)
    if not base_dir.exists() or not base_dir.is_dir():
        return model

    for path in sorted(base_dir.glob("*.json"), key=lambda item: str(item).lower()):
        try:
            bound = build_profile_bound_workflow_form_model(path)
            problems: list[str] = []
            if bound.missing_required_fields:
                problems.append("missing required values: " + ", ".join(bound.missing_required_fields))
            valid = not bound.missing_required_fields and bound.command_preview is not None
            model.profiles.append(
                ProfileLauncherCard(
                    path=str(path),
                    profile_name=bound.profile_name or path.stem,
                    preset_name=bound.preset_name or "",
                    workflow_name=bound.workflow_name,
                    valid=valid,
                    command_preview=bound.command_preview,
                    problems=tuple(problems),
                )
            )
        except Exception as exc:
            model.profiles.append(
                ProfileLauncherCard(
                    path=str(path),
                    profile_name=path.stem,
                    preset_name="",
                    workflow_name=None,
                    valid=False,
                    command_preview=None,
                    problems=(str(exc),),
                )
            )

    return model
