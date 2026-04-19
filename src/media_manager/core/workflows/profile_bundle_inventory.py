from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .profile_bundle import filter_workflow_profile_bundle, load_workflow_profile_bundle


@dataclass(slots=True, frozen=True)
class WorkflowProfileBundleRecord:
    bundle_name: str
    bundle_path: Path
    profiles_dir: str | None
    loadable: bool
    clean_bundle: bool
    profile_count: int
    valid_count: int
    invalid_count: int
    workflow_summary: dict[str, int] = field(default_factory=dict)
    preset_summary: dict[str, int] = field(default_factory=dict)
    problem_summary: dict[str, int] = field(default_factory=dict)
    duplicate_profile_name_count: int = 0
    duplicate_command_count: int = 0
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            'bundle_name': self.bundle_name,
            'bundle_path': str(self.bundle_path),
            'profiles_dir': self.profiles_dir,
            'loadable': self.loadable,
            'clean_bundle': self.clean_bundle,
            'profile_count': self.profile_count,
            'valid_count': self.valid_count,
            'invalid_count': self.invalid_count,
            'workflow_summary': dict(self.workflow_summary),
            'preset_summary': dict(self.preset_summary),
            'problem_summary': dict(self.problem_summary),
            'duplicate_profile_name_count': self.duplicate_profile_name_count,
            'duplicate_command_count': self.duplicate_command_count,
            'errors': list(self.errors),
        }


@dataclass(slots=True)
class WorkflowProfileBundleDirectoryInventory:
    bundles_dir: Path
    records: list[WorkflowProfileBundleRecord] = field(default_factory=list)

    def build_summary(self) -> dict[str, object]:
        return summarize_workflow_profile_bundle_records(self.records)

    def to_dict(self) -> dict[str, object]:
        return {
            'bundles_dir': str(self.bundles_dir),
            'summary': self.build_summary(),
            'bundles': [item.to_dict() for item in self.records],
        }


def _invalid_record(file_path: Path, message: str) -> WorkflowProfileBundleRecord:
    return WorkflowProfileBundleRecord(
        bundle_name=file_path.stem,
        bundle_path=file_path,
        profiles_dir=None,
        loadable=False,
        clean_bundle=False,
        profile_count=0,
        valid_count=0,
        invalid_count=0,
        workflow_summary={},
        preset_summary={},
        problem_summary={str(message): 1},
        duplicate_profile_name_count=0,
        duplicate_command_count=0,
        errors=(str(message),),
    )


def scan_workflow_profile_bundle_inventory(
    bundles_dir: str | Path,
    *,
    workflow_name: str | None = None,
    preset_name: str | None = None,
    only_valid: bool = False,
    only_invalid: bool = False,
) -> list[WorkflowProfileBundleRecord]:
    base_dir = Path(bundles_dir)
    if not base_dir.exists() or not base_dir.is_dir():
        return []

    records: list[WorkflowProfileBundleRecord] = []
    for file_path in sorted(base_dir.rglob('*.json'), key=lambda p: str(p).lower()):
        try:
            bundle = load_workflow_profile_bundle(file_path)
            bundle = filter_workflow_profile_bundle(
                bundle,
                workflow_name=workflow_name,
                preset_name=preset_name,
                only_valid=only_valid,
                only_invalid=only_invalid,
            )
            summary = bundle.summary.to_dict()
            records.append(
                WorkflowProfileBundleRecord(
                    bundle_name=file_path.stem,
                    bundle_path=file_path,
                    profiles_dir=bundle.profiles_dir,
                    loadable=True,
                    clean_bundle=summary['invalid_count'] == 0,
                    profile_count=summary['profile_count'],
                    valid_count=summary['valid_count'],
                    invalid_count=summary['invalid_count'],
                    workflow_summary=dict(summary.get('workflow_summary', {})),
                    preset_summary=dict(summary.get('preset_summary', {})),
                    problem_summary=dict(summary.get('problem_summary', {})),
                    duplicate_profile_name_count=int(summary.get('duplicate_profile_name_count', 0)),
                    duplicate_command_count=int(summary.get('duplicate_command_count', 0)),
                    errors=(),
                )
            )
        except Exception as exc:
            records.append(_invalid_record(file_path, str(exc)))
    return records


def filter_workflow_profile_bundle_records(
    records: list[WorkflowProfileBundleRecord],
    *,
    bundle_name: str | None = None,
    only_clean_bundles: bool = False,
    only_problematic_bundles: bool = False,
) -> list[WorkflowProfileBundleRecord]:
    filtered = list(records)
    if bundle_name:
        normalized = bundle_name.strip().lower()
        filtered = [item for item in filtered if item.bundle_name.strip().lower() == normalized]
    if only_clean_bundles and not only_problematic_bundles:
        filtered = [item for item in filtered if item.clean_bundle]
    elif only_problematic_bundles and not only_clean_bundles:
        filtered = [item for item in filtered if not item.clean_bundle]
    return filtered


def summarize_workflow_profile_bundle_records(records: list[WorkflowProfileBundleRecord]) -> dict[str, object]:
    workflow_summary: dict[str, int] = {}
    preset_summary: dict[str, int] = {}
    problem_summary: dict[str, int] = {}
    profile_count = 0
    valid_count = 0
    invalid_count = 0
    loadable_count = 0
    unreadable_count = 0
    clean_bundle_count = 0
    problematic_bundle_count = 0
    duplicate_profile_name_count = 0
    duplicate_command_count = 0

    for item in records:
        profile_count += item.profile_count
        valid_count += item.valid_count
        invalid_count += item.invalid_count
        duplicate_profile_name_count += item.duplicate_profile_name_count
        duplicate_command_count += item.duplicate_command_count
        if item.loadable:
            loadable_count += 1
        else:
            unreadable_count += 1
        if item.clean_bundle:
            clean_bundle_count += 1
        else:
            problematic_bundle_count += 1
        for key, value in item.workflow_summary.items():
            workflow_summary[key] = workflow_summary.get(key, 0) + value
        for key, value in item.preset_summary.items():
            preset_summary[key] = preset_summary.get(key, 0) + value
        if item.errors:
            for error in item.errors:
                problem_summary[error] = problem_summary.get(error, 0) + 1
        for key, value in item.problem_summary.items():
            problem_summary[key] = problem_summary.get(key, 0) + value
    return {
        'bundle_count': len(records),
        'loadable_count': loadable_count,
        'unreadable_count': unreadable_count,
        'clean_bundle_count': clean_bundle_count,
        'problematic_bundle_count': problematic_bundle_count,
        'profile_count': profile_count,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'workflow_summary': dict(sorted(workflow_summary.items())),
        'preset_summary': dict(sorted(preset_summary.items())),
        'problem_summary': dict(sorted(problem_summary.items())),
        'duplicate_profile_name_count': duplicate_profile_name_count,
        'duplicate_command_count': duplicate_command_count,
    }


def build_workflow_profile_bundle_inventory(
    bundles_dir: str | Path,
    *,
    workflow_name: str | None = None,
    preset_name: str | None = None,
    only_valid: bool = False,
    only_invalid: bool = False,
    bundle_name: str | None = None,
    only_clean_bundles: bool = False,
    only_problematic_bundles: bool = False,
) -> WorkflowProfileBundleDirectoryInventory:
    records = scan_workflow_profile_bundle_inventory(
        bundles_dir,
        workflow_name=workflow_name,
        preset_name=preset_name,
        only_valid=only_valid,
        only_invalid=only_invalid,
    )
    filtered = filter_workflow_profile_bundle_records(
        records,
        bundle_name=bundle_name,
        only_clean_bundles=only_clean_bundles,
        only_problematic_bundles=only_problematic_bundles,
    )
    return WorkflowProfileBundleDirectoryInventory(bundles_dir=Path(bundles_dir), records=filtered)
