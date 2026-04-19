from __future__ import annotations

from pathlib import Path

from media_manager.core.workflows.profile_bundle import (
    WorkflowProfileBundle,
    WorkflowProfileBundleItem,
    build_workflow_profile_bundle_items,
    build_workflow_profile_bundle_summary,
    compare_workflow_profile_bundles,
    filter_workflow_profile_bundle,
    load_workflow_profile_bundle,
    merge_workflow_profile_bundles,
    write_workflow_profile_bundle,
)
from media_manager.core.workflows.profile_inventory import WorkflowProfileRecord


def test_build_workflow_profile_bundle_items_adds_relative_paths(tmp_path: Path) -> None:
    profiles_dir = tmp_path / "profiles"
    nested = profiles_dir / "family"
    nested.mkdir(parents=True)
    profile_path = nested / "cleanup.json"

    records = [
        WorkflowProfileRecord(
            name="cleanup",
            title="Family cleanup",
            workflow_name="cleanup",
            preset_name="cleanup-family-library",
            profile_name="Family cleanup",
            profile_path=profile_path,
            valid=True,
            missing_required_fields=(),
            problems=(),
            command_preview="media-manager workflow run cleanup --source C:/Photos --target E:/Library",
        )
    ]

    items = build_workflow_profile_bundle_items(records, profiles_dir=profiles_dir)

    assert len(items) == 1
    assert items[0].relative_profile_path == "family/cleanup.json"
    assert items[0].profile_path.endswith("cleanup.json")


def test_build_workflow_profile_bundle_summary_counts_duplicates() -> None:
    items = [
        WorkflowProfileBundleItem(
            name="one",
            title="Family cleanup",
            workflow_name="cleanup",
            preset_name="cleanup-family-library",
            profile_name="Family cleanup",
            profile_path="profiles/one.json",
            relative_profile_path="one.json",
            valid=True,
            command_preview="media-manager workflow run cleanup --source C:/Photos --target E:/Library",
        ),
        WorkflowProfileBundleItem(
            name="two",
            title="Family cleanup",
            workflow_name="cleanup",
            preset_name="cleanup-family-library",
            profile_name="Family cleanup",
            profile_path="profiles/two.json",
            relative_profile_path="two.json",
            valid=True,
            command_preview="media-manager workflow run cleanup --source C:/Photos --target E:/Library",
        ),
        WorkflowProfileBundleItem(
            name="bad",
            title="Bad duplicates",
            workflow_name="duplicates",
            preset_name="duplicates-similar-review",
            profile_name="Bad duplicates",
            profile_path="profiles/bad.json",
            relative_profile_path="bad.json",
            valid=False,
            problems=("duplicates apply requires yes",),
            command_preview=None,
        ),
    ]

    summary = build_workflow_profile_bundle_summary(items)

    assert summary.profile_count == 3
    assert summary.valid_count == 2
    assert summary.invalid_count == 1
    assert summary.workflow_summary["cleanup"] == 2
    assert summary.preset_summary["cleanup-family-library"] == 2
    assert summary.problem_summary["duplicates apply requires yes"] == 1
    assert summary.duplicate_profile_name_summary["Family cleanup"] == 2
    assert summary.duplicate_profile_name_count == 2
    assert summary.duplicate_command_count == 2


def test_write_and_load_workflow_profile_bundle_roundtrip(tmp_path: Path) -> None:
    bundle_path = tmp_path / "exports" / "profiles-bundle.json"
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "trip.json").write_text(
        "\n".join(
            [
                "{",
                '  "schema_version": 1,',
                '  "profile_name": "Italy trip",',
                '  "preset": "trip-hardlink-collection",',
                '  "values": {',
                '    "source": ["C:/Phone"],',
                '    "target": "E:/Trips",',
                '    "label": "Italy_2025",',
                '    "start": "2025-08-01",',
                '    "end": "2025-08-14"',
                "  }",
                "}",
            ]
        ),
        encoding="utf-8",
    )

    written = write_workflow_profile_bundle(bundle_path, profiles_dir)
    loaded = load_workflow_profile_bundle(written)

    assert written.exists()
    assert loaded.summary.profile_count == 1
    assert loaded.summary.valid_count == 1
    assert loaded.profiles[0].profile_name == "Italy trip"
    assert loaded.profiles[0].relative_profile_path == "trip.json"


def test_filter_workflow_profile_bundle_recomputes_summary() -> None:
    bundle = WorkflowProfileBundle(
        profiles_dir="profiles",
        workflow_filter=None,
        preset_filter=None,
        only_valid=False,
        only_invalid=False,
        summary=build_workflow_profile_bundle_summary(
            [
                WorkflowProfileBundleItem(
                    name="cleanup",
                    title="Cleanup",
                    workflow_name="cleanup",
                    preset_name="cleanup-family-library",
                    profile_name="Cleanup",
                    profile_path="profiles/cleanup.json",
                    relative_profile_path="cleanup.json",
                    valid=True,
                    command_preview="cleanup-cmd",
                ),
                WorkflowProfileBundleItem(
                    name="duplicates",
                    title="Duplicates",
                    workflow_name="duplicates",
                    preset_name="duplicates-similar-review",
                    profile_name="Duplicates",
                    profile_path="profiles/duplicates.json",
                    relative_profile_path="duplicates.json",
                    valid=False,
                    problems=("duplicates apply requires yes",),
                ),
            ]
        ),
        profiles=[
            WorkflowProfileBundleItem(
                name="cleanup",
                title="Cleanup",
                workflow_name="cleanup",
                preset_name="cleanup-family-library",
                profile_name="Cleanup",
                profile_path="profiles/cleanup.json",
                relative_profile_path="cleanup.json",
                valid=True,
                command_preview="cleanup-cmd",
            ),
            WorkflowProfileBundleItem(
                name="duplicates",
                title="Duplicates",
                workflow_name="duplicates",
                preset_name="duplicates-similar-review",
                profile_name="Duplicates",
                profile_path="profiles/duplicates.json",
                relative_profile_path="duplicates.json",
                valid=False,
                problems=("duplicates apply requires yes",),
            ),
        ],
    )

    filtered = filter_workflow_profile_bundle(bundle, workflow_name="duplicates", only_invalid=True)

    assert filtered.summary.profile_count == 1
    assert filtered.summary.invalid_count == 1
    assert filtered.summary.valid_count == 0
    assert filtered.workflow_filter == "duplicates"
    assert filtered.only_invalid is True
    assert filtered.profiles[0].workflow_name == "duplicates"


def test_merge_workflow_profile_bundles_prefers_last_version() -> None:
    first = WorkflowProfileBundle(
        profiles_dir="first",
        workflow_filter=None,
        preset_filter=None,
        only_valid=False,
        only_invalid=False,
        summary=build_workflow_profile_bundle_summary([]),
        profiles=[
            WorkflowProfileBundleItem(
                name="cleanup",
                title="Family cleanup",
                workflow_name="cleanup",
                preset_name="cleanup-family-library",
                profile_name="Family cleanup",
                profile_path="first/family.json",
                relative_profile_path="family.json",
                valid=True,
                command_preview="first-command",
            )
        ],
    )
    second = WorkflowProfileBundle(
        profiles_dir="second",
        workflow_filter=None,
        preset_filter=None,
        only_valid=False,
        only_invalid=False,
        summary=build_workflow_profile_bundle_summary([]),
        profiles=[
            WorkflowProfileBundleItem(
                name="cleanup",
                title="Family cleanup updated",
                workflow_name="cleanup",
                preset_name="cleanup-family-library",
                profile_name="Family cleanup updated",
                profile_path="second/family.json",
                relative_profile_path="family.json",
                valid=True,
                command_preview="second-command",
            )
        ],
    )

    merged = merge_workflow_profile_bundles([first, second], prefer="last")

    assert merged.summary.profile_count == 1
    assert merged.profiles[0].title == "Family cleanup updated"
    assert merged.profiles[0].command_preview == "second-command"


def test_compare_workflow_profile_bundles_counts_changes() -> None:
    left = WorkflowProfileBundle(
        profiles_dir="left",
        workflow_filter=None,
        preset_filter=None,
        only_valid=False,
        only_invalid=False,
        summary=build_workflow_profile_bundle_summary([]),
        profiles=[
            WorkflowProfileBundleItem(
                name="cleanup",
                title="Cleanup",
                workflow_name="cleanup",
                preset_name="cleanup-family-library",
                profile_name="Cleanup",
                profile_path="left/cleanup.json",
                relative_profile_path="cleanup.json",
                valid=True,
                command_preview="cleanup-command",
            ),
            WorkflowProfileBundleItem(
                name="trip",
                title="Trip",
                workflow_name="trip",
                preset_name="trip-hardlink-collection",
                profile_name="Trip",
                profile_path="left/trip.json",
                relative_profile_path="trip.json",
                valid=True,
                command_preview="trip-command",
            ),
        ],
    )
    right = WorkflowProfileBundle(
        profiles_dir="right",
        workflow_filter=None,
        preset_filter=None,
        only_valid=False,
        only_invalid=False,
        summary=build_workflow_profile_bundle_summary([]),
        profiles=[
            WorkflowProfileBundleItem(
                name="cleanup",
                title="Cleanup",
                workflow_name="cleanup",
                preset_name="cleanup-family-library",
                profile_name="Cleanup",
                profile_path="right/cleanup.json",
                relative_profile_path="cleanup.json",
                valid=False,
                problems=("missing target",),
                command_preview=None,
            ),
            WorkflowProfileBundleItem(
                name="duplicates",
                title="Duplicates",
                workflow_name="duplicates",
                preset_name="duplicates-similar-review",
                profile_name="Duplicates",
                profile_path="right/duplicates.json",
                relative_profile_path="duplicates.json",
                valid=True,
                command_preview="duplicates-command",
            ),
        ],
    )

    comparison = compare_workflow_profile_bundles(left, right)

    assert comparison.summary.left_profile_count == 2
    assert comparison.summary.right_profile_count == 2
    assert comparison.summary.added_count == 1
    assert comparison.summary.removed_count == 1
    assert comparison.summary.changed_count == 1
    assert comparison.summary.unchanged_count == 0
    assert comparison.summary.changed_validity_count == 1
    assert comparison.summary.changed_command_count == 1
    assert comparison.summary.changed_problem_count == 1
    statuses = {item.key: item.status for item in comparison.entries}
    assert statuses["cleanup.json"] == "changed"
    assert statuses["duplicates.json"] == "added"
    assert statuses["trip.json"] == "removed"
