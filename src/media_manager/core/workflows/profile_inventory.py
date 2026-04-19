from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .presets import load_workflow_profile, validate_workflow_profile


@dataclass(slots=True, frozen=True)
class WorkflowProfileRecord:
    name: str
    title: str
    workflow_name: str
    preset_name: str | None
    profile_name: str | None
    profile_path: Path
    valid: bool
    missing_required_fields: tuple[str, ...] = ()
    problems: tuple[str, ...] = ()
    command_preview: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "title": self.title,
            "workflow_name": self.workflow_name,
            "preset_name": self.preset_name,
            "profile_name": self.profile_name,
            "profile_path": str(self.profile_path),
            "valid": self.valid,
            "missing_required_fields": list(self.missing_required_fields),
            "problems": list(self.problems),
            "command_preview": self.command_preview,
        }


@dataclass(slots=True)
class WorkflowProfileInventory:
    profiles_dir: Path
    records: list[WorkflowProfileRecord] = field(default_factory=list)

    def build_summary(self) -> dict[str, object]:
        return summarize_workflow_profile_records(self.records)

    def to_dict(self) -> dict[str, object]:
        return {
            "profiles_dir": str(self.profiles_dir),
            "summary": self.build_summary(),
            "profiles": [item.to_dict() for item in self.records],
        }


def _invalid_record(file_path: Path, message: str) -> WorkflowProfileRecord:
    return WorkflowProfileRecord(
        name=file_path.stem,
        title=file_path.stem,
        workflow_name="unknown",
        preset_name=None,
        profile_name=None,
        profile_path=file_path,
        valid=False,
        missing_required_fields=(),
        problems=(str(message),),
        command_preview=None,
    )


def scan_workflow_profile_inventory(profiles_dir: str | Path) -> list[WorkflowProfileRecord]:
    base_path = Path(profiles_dir)
    if not base_path.exists() or not base_path.is_dir():
        return []

    records: list[WorkflowProfileRecord] = []
    for file_path in sorted(base_path.rglob("*.json"), key=lambda item: str(item).lower()):
        try:
            profile = load_workflow_profile(file_path)
            validation = validate_workflow_profile(profile)
            records.append(
                WorkflowProfileRecord(
                    name=file_path.stem,
                    title=profile.profile_name or file_path.stem,
                    workflow_name=validation.workflow_name or "unknown",
                    preset_name=profile.preset_name,
                    profile_name=profile.profile_name,
                    profile_path=file_path,
                    valid=validation.valid,
                    missing_required_fields=tuple(validation.missing_values),
                    problems=tuple(validation.problems),
                    command_preview=validation.command_preview,
                )
            )
        except Exception as exc:
            records.append(_invalid_record(file_path, str(exc)))
    return records


def filter_workflow_profile_records(
    records: list[WorkflowProfileRecord],
    *,
    workflow_name: str | None = None,
    preset_name: str | None = None,
    only_valid: bool = False,
    only_invalid: bool = False,
) -> list[WorkflowProfileRecord]:
    filtered = list(records)

    if workflow_name:
        normalized = workflow_name.strip().lower()
        filtered = [item for item in filtered if item.workflow_name.strip().lower() == normalized]

    if preset_name:
        normalized = preset_name.strip().lower()
        filtered = [
            item
            for item in filtered
            if (item.preset_name or "").strip().lower() == normalized
        ]

    if only_valid and not only_invalid:
        filtered = [item for item in filtered if item.valid]
    elif only_invalid and not only_valid:
        filtered = [item for item in filtered if not item.valid]

    return filtered


def summarize_workflow_profile_records(records: list[WorkflowProfileRecord]) -> dict[str, object]:
    workflow_summary: dict[str, int] = {}
    preset_summary: dict[str, int] = {}
    problem_summary: dict[str, int] = {}
    valid_count = 0
    invalid_count = 0

    for item in records:
        workflow_summary[item.workflow_name] = workflow_summary.get(item.workflow_name, 0) + 1
        if item.preset_name:
            preset_summary[item.preset_name] = preset_summary.get(item.preset_name, 0) + 1
        if item.valid:
            valid_count += 1
        else:
            invalid_count += 1
            for problem in item.problems:
                problem_summary[problem] = problem_summary.get(problem, 0) + 1

    return {
        "profile_count": len(records),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "workflow_summary": dict(sorted(workflow_summary.items())),
        "preset_summary": dict(sorted(preset_summary.items())),
        "problem_summary": dict(sorted(problem_summary.items())),
    }


def build_workflow_profile_inventory(
    profiles_dir: str | Path,
    *,
    workflow_name: str | None = None,
    preset_name: str | None = None,
    only_valid: bool = False,
    only_invalid: bool = False,
) -> WorkflowProfileInventory:
    records = scan_workflow_profile_inventory(profiles_dir)
    filtered = filter_workflow_profile_records(
        records,
        workflow_name=workflow_name,
        preset_name=preset_name,
        only_valid=only_valid,
        only_invalid=only_invalid,
    )
    return WorkflowProfileInventory(profiles_dir=Path(profiles_dir), records=filtered)
