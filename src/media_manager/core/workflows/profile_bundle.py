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


@dataclass(slots=True, frozen=True)
class WorkflowProfileBundleComparisonEntry:
    key: str
    status: str
    left_item: WorkflowProfileBundleItem | None = None
    right_item: WorkflowProfileBundleItem | None = None
    validity_changed: bool = False
    command_changed: bool = False
    problems_changed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "status": self.status,
            "left_item": None if self.left_item is None else self.left_item.to_dict(),
            "right_item": None if self.right_item is None else self.right_item.to_dict(),
            "validity_changed": self.validity_changed,
            "command_changed": self.command_changed,
            "problems_changed": self.problems_changed,
        }


@dataclass(slots=True, frozen=True)
class WorkflowProfileBundleComparisonSummary:
    left_profile_count: int
    right_profile_count: int
    added_count: int
    removed_count: int
    changed_count: int
    unchanged_count: int
    changed_validity_count: int = 0
    changed_command_count: int = 0
    changed_problem_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "left_profile_count": self.left_profile_count,
            "right_profile_count": self.right_profile_count,
            "added_count": self.added_count,
            "removed_count": self.removed_count,
            "changed_count": self.changed_count,
            "unchanged_count": self.unchanged_count,
            "changed_validity_count": self.changed_validity_count,
            "changed_command_count": self.changed_command_count,
            "changed_problem_count": self.changed_problem_count,
        }


@dataclass(slots=True)
class WorkflowProfileBundleComparison:
    left_profiles_dir: str
    right_profiles_dir: str
    summary: WorkflowProfileBundleComparisonSummary
    entries: list[WorkflowProfileBundleComparisonEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "left_profiles_dir": self.left_profiles_dir,
            "right_profiles_dir": self.right_profiles_dir,
            "summary": self.summary.to_dict(),
            "entries": [item.to_dict() for item in self.entries],
        }


def _safe_relative_path(profile_path: Path, base_dir: Path) -> str:
    try:
        return profile_path.relative_to(base_dir).as_posix()
    except ValueError:
        return profile_path.name


def _bundle_item_key(item: WorkflowProfileBundleItem) -> str:
    return item.relative_profile_path or item.profile_path or item.name


def _sort_bundle_items(items: list[WorkflowProfileBundleItem]) -> list[WorkflowProfileBundleItem]:
    return sorted(items, key=lambda item: (_bundle_item_key(item).lower(), item.name.lower(), item.title.lower()))


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
    return _sort_bundle_items(items)


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


def filter_workflow_profile_bundle(
    bundle: WorkflowProfileBundle,
    *,
    workflow_name: str | None = None,
    preset_name: str | None = None,
    only_valid: bool = False,
    only_invalid: bool = False,
) -> WorkflowProfileBundle:
    filtered = list(bundle.profiles)

    if workflow_name:
        normalized = workflow_name.strip().lower()
        filtered = [item for item in filtered if item.workflow_name.strip().lower() == normalized]

    if preset_name:
        normalized = preset_name.strip().lower()
        filtered = [item for item in filtered if (item.preset_name or "").strip().lower() == normalized]

    if only_valid and not only_invalid:
        filtered = [item for item in filtered if item.valid]
    elif only_invalid and not only_valid:
        filtered = [item for item in filtered if not item.valid]

    filtered = _sort_bundle_items(filtered)
    return WorkflowProfileBundle(
        profiles_dir=bundle.profiles_dir,
        workflow_filter=workflow_name,
        preset_filter=preset_name,
        only_valid=only_valid,
        only_invalid=only_invalid,
        summary=build_workflow_profile_bundle_summary(filtered),
        profiles=filtered,
    )


def merge_workflow_profile_bundles(
    bundles: list[WorkflowProfileBundle],
    *,
    prefer: str = "last",
    profiles_dir: str = "merged",
) -> WorkflowProfileBundle:
    if prefer not in {"first", "last"}:
        raise ValueError("Bundle merge preference must be either 'first' or 'last'.")

    merged: dict[str, WorkflowProfileBundleItem] = {}
    for bundle in bundles:
        for item in bundle.profiles:
            key = _bundle_item_key(item)
            if prefer == "first" and key in merged:
                continue
            merged[key] = item

    items = _sort_bundle_items(list(merged.values()))
    return WorkflowProfileBundle(
        profiles_dir=profiles_dir,
        workflow_filter=None,
        preset_filter=None,
        only_valid=False,
        only_invalid=False,
        summary=build_workflow_profile_bundle_summary(items),
        profiles=items,
    )


def compare_workflow_profile_bundles(
    left: WorkflowProfileBundle,
    right: WorkflowProfileBundle,
) -> WorkflowProfileBundleComparison:
    left_map = {_bundle_item_key(item): item for item in left.profiles}
    right_map = {_bundle_item_key(item): item for item in right.profiles}
    keys = sorted(set(left_map) | set(right_map), key=str.lower)

    entries: list[WorkflowProfileBundleComparisonEntry] = []
    added_count = 0
    removed_count = 0
    changed_count = 0
    unchanged_count = 0
    changed_validity_count = 0
    changed_command_count = 0
    changed_problem_count = 0

    for key in keys:
        left_item = left_map.get(key)
        right_item = right_map.get(key)

        if left_item is None and right_item is not None:
            entries.append(
                WorkflowProfileBundleComparisonEntry(
                    key=key,
                    status="added",
                    left_item=None,
                    right_item=right_item,
                )
            )
            added_count += 1
            continue

        if right_item is None and left_item is not None:
            entries.append(
                WorkflowProfileBundleComparisonEntry(
                    key=key,
                    status="removed",
                    left_item=left_item,
                    right_item=None,
                )
            )
            removed_count += 1
            continue

        assert left_item is not None and right_item is not None
        validity_changed = left_item.valid != right_item.valid
        command_changed = left_item.command_preview != right_item.command_preview
        problems_changed = left_item.problems != right_item.problems

        changed = (
            validity_changed
            or command_changed
            or problems_changed
            or left_item.profile_name != right_item.profile_name
            or left_item.preset_name != right_item.preset_name
            or left_item.workflow_name != right_item.workflow_name
            or left_item.missing_required_fields != right_item.missing_required_fields
        )

        entries.append(
            WorkflowProfileBundleComparisonEntry(
                key=key,
                status="changed" if changed else "unchanged",
                left_item=left_item,
                right_item=right_item,
                validity_changed=validity_changed,
                command_changed=command_changed,
                problems_changed=problems_changed,
            )
        )

        if changed:
            changed_count += 1
            if validity_changed:
                changed_validity_count += 1
            if command_changed:
                changed_command_count += 1
            if problems_changed:
                changed_problem_count += 1
        else:
            unchanged_count += 1

    summary = WorkflowProfileBundleComparisonSummary(
        left_profile_count=len(left.profiles),
        right_profile_count=len(right.profiles),
        added_count=added_count,
        removed_count=removed_count,
        changed_count=changed_count,
        unchanged_count=unchanged_count,
        changed_validity_count=changed_validity_count,
        changed_command_count=changed_command_count,
        changed_problem_count=changed_problem_count,
    )
    return WorkflowProfileBundleComparison(
        left_profiles_dir=left.profiles_dir,
        right_profiles_dir=right.profiles_dir,
        summary=summary,
        entries=entries,
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
    file_path.write_text(json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return file_path


def load_workflow_profile_bundle(path: str | Path) -> WorkflowProfileBundle:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    summary_payload = payload.get("summary", {})
    profiles_payload = payload.get("profiles", [])
    summary = WorkflowProfileBundleSummary(
        profile_count=int(summary_payload.get("profile_count", 0)),
        valid_count=int(summary_payload.get("valid_count", 0)),
        invalid_count=int(summary_payload.get("invalid_count", 0)),
        workflow_summary=dict(summary_payload.get("workflow_summary", {})),
        preset_summary=dict(summary_payload.get("preset_summary", {})),
        problem_summary=dict(summary_payload.get("problem_summary", {})),
        duplicate_profile_name_summary=dict(summary_payload.get("duplicate_profile_name_summary", {})),
        duplicate_command_summary=dict(summary_payload.get("duplicate_command_summary", {})),
        duplicate_profile_name_count=int(summary_payload.get("duplicate_profile_name_count", 0)),
        duplicate_command_count=int(summary_payload.get("duplicate_command_count", 0)),
    )
    profiles = [
        WorkflowProfileBundleItem(
            name=str(item.get("name", "")),
            title=str(item.get("title", "")),
            workflow_name=str(item.get("workflow_name", "unknown")),
            preset_name=item.get("preset_name"),
            profile_name=item.get("profile_name"),
            profile_path=str(item.get("profile_path", "")),
            relative_profile_path=str(item.get("relative_profile_path", "")),
            valid=bool(item.get("valid", False)),
            missing_required_fields=tuple(item.get("missing_required_fields", [])),
            problems=tuple(item.get("problems", [])),
            command_preview=item.get("command_preview"),
        )
        for item in profiles_payload
    ]
    return WorkflowProfileBundle(
        profiles_dir=str(payload.get("profiles_dir", "")),
        workflow_filter=payload.get("workflow_filter"),
        preset_filter=payload.get("preset_filter"),
        only_valid=bool(payload.get("only_valid", False)),
        only_invalid=bool(payload.get("only_invalid", False)),
        summary=summary,
        profiles=profiles,
    )
