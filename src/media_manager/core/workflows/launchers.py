from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from .forms import build_preset_bound_workflow_form_model, build_profile_bound_workflow_form_model
from .presets import list_workflow_presets


@dataclass(slots=True, frozen=True)
class WorkflowLauncher:
    launcher_type: str
    name: str
    title: str
    workflow_name: str
    preset_name: str | None
    profile_name: str | None
    profile_path: str | None
    valid: bool
    missing_required_fields: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()
    command_preview: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "launcher_type": self.launcher_type,
            "name": self.name,
            "title": self.title,
            "workflow_name": self.workflow_name,
            "preset_name": self.preset_name,
            "profile_name": self.profile_name,
            "profile_path": self.profile_path,
            "valid": self.valid,
            "missing_required_fields": list(self.missing_required_fields),
            "problems": list(self.problems),
            "command_preview": self.command_preview,
        }


@dataclass(slots=True)
class WorkflowLauncherModel:
    launchers: list[WorkflowLauncher] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"launchers": [item.to_dict() for item in self.launchers]}


def build_preset_launchers() -> list[WorkflowLauncher]:
    items: list[WorkflowLauncher] = []
    for preset in list_workflow_presets():
        bound = build_preset_bound_workflow_form_model(preset.name)
        items.append(
            WorkflowLauncher(
                launcher_type="preset",
                name=preset.name,
                title=preset.title,
                workflow_name=bound.workflow_name,
                preset_name=preset.name,
                profile_name=None,
                profile_path=None,
                valid=bound.valid,
                missing_required_fields=bound.missing_required_fields,
                problems=bound.problems,
                command_preview=bound.command_preview,
            )
        )
    return items


def build_profile_launchers(profiles_dir: str | Path) -> list[WorkflowLauncher]:
    base_path = Path(profiles_dir)
    if not base_path.exists() or not base_path.is_dir():
        return []

    items: list[WorkflowLauncher] = []
    for file_path in sorted(base_path.rglob("*.json"), key=lambda p: str(p).lower()):
        try:
            bound = build_profile_bound_workflow_form_model(file_path)
            items.append(
                WorkflowLauncher(
                    launcher_type="profile",
                    name=file_path.stem,
                    title=bound.profile_name or file_path.stem,
                    workflow_name=bound.workflow_name,
                    preset_name=bound.preset_name,
                    profile_name=bound.profile_name,
                    profile_path=str(file_path),
                    valid=bound.valid,
                    missing_required_fields=bound.missing_required_fields,
                    problems=bound.problems,
                    command_preview=bound.command_preview,
                )
            )
        except Exception as exc:
            items.append(
                WorkflowLauncher(
                    launcher_type="profile",
                    name=file_path.stem,
                    title=file_path.stem,
                    workflow_name="unknown",
                    preset_name=None,
                    profile_name=None,
                    profile_path=str(file_path),
                    valid=False,
                    missing_required_fields=(),
                    problems=(str(exc),),
                    command_preview=None,
                )
            )
    return items


def build_workflow_launcher_model(profiles_dir: str | Path | None = None) -> WorkflowLauncherModel:
    launchers = build_preset_launchers()
    if profiles_dir is not None:
        launchers.extend(build_profile_launchers(profiles_dir))

    launchers.sort(key=lambda item: (item.launcher_type, item.title.lower(), item.name.lower()))
    return WorkflowLauncherModel(launchers=launchers)
