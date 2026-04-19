from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from .profile_inventory import WorkflowProfileRecord, build_workflow_profile_inventory


@dataclass(slots=True, frozen=True)
class WorkflowProfileBundleItem:
    name: str
    title: str
    workflow_name: str
    preset_name: str | None
    profile_name: str | None
    profile_path: str
    relative_profile_path: str
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
            "profile_path": self.profile_path,
            "relative_profile_path": self.relative_profile_path,
            "valid": self.valid,
            "missing_required_fields": list(self.missing_required_fields),
            "problems": list(self.problems),
            "command_preview": self.command_preview,
        }


@dataclass(slots=True, frozen=True)
class WorkflowProfileBundleSummary:
    profile_count: int
    valid_count: int
    invalid_count: int
    workflow_summary: dict[str, int] = field(default_factory=dict)
    preset_summary: dict[str, int] = field(default_factory=dict)
    problem_summary: dict[str, int] = field(default_factory=dict)
    duplicate_profile_name_summary: dict[str, int] = field(default_factory=dict)
    duplicate_command_summary: dict[str, int] = field(default_factory=dict)
    duplicate_profile_name_count: int = 0
    duplicate_command_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_count": self.profile_count,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "workflow_summary": dict(self.workflow_summary),
            "preset_summary": dict(self.preset_summary),
            "problem_summary": dict(self.problem_summary),
            "duplicate_profile_name_summary": dict(self.duplicate_profile_name_summary),
            "duplicate_command_summary": dict(self.duplicate_command_summary),
            "duplicate_profile_name_count": self.duplicate_profile_name_count,
            "duplicate_command_count": self.duplicate_command_count,
        }


@dataclass(slots=True)
class WorkflowProfileBundle:
    profiles_dir: str
    workflow_filter: str | None
    preset_filter: str | None
    only_valid: bool
    only_invalid: bool
    summary: WorkflowProfileBundleSummary
    profiles: list[WorkflowProfileBundleItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "profiles_dir": self.profiles_dir,
            "workflow_filter": self.workflow_filter,
            "preset_filter": self.preset_filter,
            "only_valid": self.only_valid,
            "only_invalid": self.only_invalid,
            "summary": self.summary.to_dict(),
            "profiles": [item.to_dict() for item in self.profiles],
        }


def _safe_relative_path(profile_path: Path, base_dir: Path) -> str:
    try:
        return profile_path.relative_to(base_dir).as_posix()
    except ValueError:
        return profile_path.name


def build_workflow_profile_bundle_items(records: list[WorkflowProfileRecord], *, profiles_dir: str | Path) -> list[WorkflowProfileBundleItem]:
    base_dir = Path(profiles_dir)
    items: list[WorkflowProfileBundleItem] = []
    for item in records:
        items.append(
            WorkflowProfileBundleItem(
                name=item.name,
                title=item.title,
                workflow_name=item.workflow_name,
                preset_name=item.preset_name,
                profile_name=item.profile_name,
                profile_path=str(item.profile_path),
                relative_profile_path=_safe_relative_path(item.profile_path, base_dir),
                valid=item.valid,
                missing_required_fields=tuple(item.missing_required_fields),
                problems=tuple(item.problems),
                command_preview=item.command_preview,
            )
        )
    return items


def build_workflow_profile_bundle_summary(items: list[WorkflowProfileBundleItem]) -> WorkflowProfileBundleSummary:
    workflow_summary: Counter[str] = Counter()
    preset_summary: Counter[str] = Counter()
    problem_summary: Counter[str] = Counter()
    profile_name_counter: Counter[str] = Counter()
    command_counter: Counter[str] = Counter()
    valid_count = 0
    invalid_count = 0

    for item in items:
        workflow_summary[item.workflow_name] += 1
        if item.preset_name:
            preset_summary[item.preset_name] += 1
        if item.profile_name:
            profile_name_counter[item.profile_name] += 1
        if item.command_preview:
            command_counter[item.command_preview] += 1
        if item.valid:
            valid_count += 1
        else:
            invalid_count += 1
            for problem in item.problems:
                problem_summary[problem] += 1

    duplicate_profile_name_summary = {key: value for key, value in sorted(profile_name_counter.items()) if value > 1}
    duplicate_command_summary = {key: value for key, value in sorted(command_counter.items()) if value > 1}

    return WorkflowProfileBundleSummary(
        profile_count=len(items),
        valid_count=valid_count,
        invalid_count=invalid_count,
        workflow_summary=dict(sorted(workflow_summary.items())),
        preset_summary=dict(sorted(preset_summary.items())),
        problem_summary=dict(sorted(problem_summary.items())),
        duplicate_profile_name_summary=duplicate_profile_name_summary,
        duplicate_command_summary=duplicate_command_summary,
        duplicate_profile_name_count=sum(duplicate_profile_name_summary.values()),
        duplicate_command_count=sum(duplicate_command_summary.values()),
    )


def build_workflow_profile_bundle(
    profiles_dir: str | Path,
    *,
    workflow_name: str | None = None,
    preset_name: str | None = None,
    only_valid: bool = False,
    only_invalid: bool = False,
) -> WorkflowProfileBundle:
    inventory = build_workflow_profile_inventory(
        profiles_dir,
        workflow_name=workflow_name,
        preset_name=preset_name,
        only_valid=only_valid,
        only_invalid=only_invalid,
    )
    items = build_workflow_profile_bundle_items(inventory.records, profiles_dir=profiles_dir)
    return WorkflowProfileBundle(
        profiles_dir=str(profiles_dir),
        workflow_filter=workflow_name,
        preset_filter=preset_name,
        only_valid=only_valid,
        only_invalid=only_invalid,
        summary=build_workflow_profile_bundle_summary(items),
        profiles=items,
    )


def write_workflow_profile_bundle(
    path: str | Path,
    profiles_dir: str | Path,
    *,
    workflow_name: str | None = None,
    preset_name: str | None = None,
    only_valid: bool = False,
    only_invalid: bool = False,
) -> Path:
    bundle = build_workflow_profile_bundle(
        profiles_dir,
        workflow_name=workflow_name,
        preset_name=preset_name,
        only_valid=only_valid,
        only_invalid=only_invalid,
    )
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False), encoding='utf-8')
    return file_path


def load_workflow_profile_bundle(path: str | Path) -> WorkflowProfileBundle:
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    summary_payload = payload.get('summary', {})
    profiles_payload = payload.get('profiles', [])
    summary = WorkflowProfileBundleSummary(
        profile_count=int(summary_payload.get('profile_count', 0)),
        valid_count=int(summary_payload.get('valid_count', 0)),
        invalid_count=int(summary_payload.get('invalid_count', 0)),
        workflow_summary=dict(summary_payload.get('workflow_summary', {})),
        preset_summary=dict(summary_payload.get('preset_summary', {})),
        problem_summary=dict(summary_payload.get('problem_summary', {})),
        duplicate_profile_name_summary=dict(summary_payload.get('duplicate_profile_name_summary', {})),
        duplicate_command_summary=dict(summary_payload.get('duplicate_command_summary', {})),
        duplicate_profile_name_count=int(summary_payload.get('duplicate_profile_name_count', 0)),
        duplicate_command_count=int(summary_payload.get('duplicate_command_count', 0)),
    )
    profiles = [
        WorkflowProfileBundleItem(
            name=str(item.get('name', '')),
            title=str(item.get('title', '')),
            workflow_name=str(item.get('workflow_name', 'unknown')),
            preset_name=item.get('preset_name'),
            profile_name=item.get('profile_name'),
            profile_path=str(item.get('profile_path', '')),
            relative_profile_path=str(item.get('relative_profile_path', '')),
            valid=bool(item.get('valid', False)),
            missing_required_fields=tuple(item.get('missing_required_fields', [])),
            problems=tuple(item.get('problems', [])),
            command_preview=item.get('command_preview'),
        )
        for item in profiles_payload
    ]
    return WorkflowProfileBundle(
        profiles_dir=str(payload.get('profiles_dir', '')),
        workflow_filter=payload.get('workflow_filter'),
        preset_filter=payload.get('preset_filter'),
        only_valid=bool(payload.get('only_valid', False)),
        only_invalid=bool(payload.get('only_invalid', False)),
        summary=summary,
        profiles=profiles,
    )
