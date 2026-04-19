from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .forms import build_preset_bound_workflow_form_model
from .presets import list_workflow_presets
from .profile_inventory import scan_workflow_profile_inventory


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

    def build_summary(self) -> dict[str, object]:
        launcher_type_summary: dict[str, int] = {}
        workflow_summary: dict[str, int] = {}
        valid_count = 0
        invalid_count = 0
        for item in self.launchers:
            launcher_type_summary[item.launcher_type] = launcher_type_summary.get(item.launcher_type, 0) + 1
            workflow_summary[item.workflow_name] = workflow_summary.get(item.workflow_name, 0) + 1
            if item.valid:
                valid_count += 1
            else:
                invalid_count += 1
        return {
            "total_launchers": len(self.launchers),
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "launcher_type_summary": dict(sorted(launcher_type_summary.items())),
            "workflow_summary": dict(sorted(workflow_summary.items())),
        }

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": self.build_summary(),
            "launchers": [item.to_dict() for item in self.launchers],
        }


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
    items: list[WorkflowLauncher] = []
    for record in scan_workflow_profile_inventory(profiles_dir):
        items.append(
            WorkflowLauncher(
                launcher_type="profile",
                name=record.name,
                title=record.title,
                workflow_name=record.workflow_name,
                preset_name=record.preset_name,
                profile_name=record.profile_name,
                profile_path=str(record.profile_path),
                valid=record.valid,
                missing_required_fields=record.missing_required_fields,
                problems=record.problems,
                command_preview=record.command_preview,
            )
        )
    return items


def build_workflow_launcher_model(profiles_dir: str | Path | None = None) -> WorkflowLauncherModel:
    launchers = build_preset_launchers()
    if profiles_dir is not None:
        launchers.extend(build_profile_launchers(profiles_dir))

    launchers.sort(key=lambda item: (item.launcher_type, item.title.lower(), item.name.lower()))
    return WorkflowLauncherModel(launchers=launchers)
