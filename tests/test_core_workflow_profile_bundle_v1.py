from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows.profile_bundle import (
    WorkflowProfileBundleItem,
    build_workflow_profile_bundle,
    build_workflow_profile_bundle_items,
    build_workflow_profile_bundle_summary,
    compare_workflow_profile_bundles,
    extract_workflow_profile_bundle,
    filter_workflow_profile_bundle,
    load_workflow_profile_bundle,
    merge_workflow_profile_bundles,
    sync_workflow_profile_bundle,
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


def test_filter_workflow_profile_bundle_filters_invalid_profiles(tmp_path: Path) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "ok.json").write_text(
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
    (profiles_dir / "bad.json").write_text(
        "\n".join(
            [
                "{",
                '  "schema_version": 1,',
                '  "profile_name": "Bad duplicates",',
                '  "preset": "duplicates-similar-review",',
                '  "values": {',
                '    "source": ["C:/Photos"],',
                '    "show_similar_review": true,',
                '    "similar_images": false',
                "  }",
                "}",
            ]
        ),
        encoding="utf-8",
    )

    bundle = build_workflow_profile_bundle(profiles_dir)
    filtered = filter_workflow_profile_bundle(bundle, only_invalid=True)

    assert filtered.summary.profile_count == 1
    assert filtered.summary.invalid_count == 1
    assert filtered.profiles[0].profile_name == "Bad duplicates"


def test_merge_workflow_profile_bundles_prefers_last_by_default() -> None:
    left = WorkflowProfileBundleItem(
        name="trip",
        title="Trip one",
        workflow_name="trip",
        preset_name="trip-hardlink-collection",
        profile_name="Trip one",
        profile_path="left/trip.json",
        relative_profile_path="trip.json",
        valid=True,
        command_preview="media-manager workflow run trip --label One",
    )
    right = WorkflowProfileBundleItem(
        name="trip",
        title="Trip two",
        workflow_name="trip",
        preset_name="trip-hardlink-collection",
        profile_name="Trip two",
        profile_path="right/trip.json",
        relative_profile_path="trip.json",
        valid=True,
        command_preview="media-manager workflow run trip --label Two",
    )

    from media_manager.core.workflows.profile_bundle import WorkflowProfileBundle, WorkflowProfileBundleSummary

    empty_summary = WorkflowProfileBundleSummary(profile_count=0, valid_count=0, invalid_count=0)
    merged = merge_workflow_profile_bundles([
        WorkflowProfileBundle("left", None, None, False, False, empty_summary, [left]),
        WorkflowProfileBundle("right", None, None, False, False, empty_summary, [right]),
    ])

    assert merged.summary.profile_count == 1
    assert merged.profiles[0].profile_name == "Trip two"


def test_compare_workflow_profile_bundles_reports_changed_validity() -> None:
    left = WorkflowProfileBundleItem(
        name="trip",
        title="Italy trip",
        workflow_name="trip",
        preset_name="trip-hardlink-collection",
        profile_name="Italy trip",
        profile_path="left/trip.json",
        relative_profile_path="trip.json",
        valid=True,
        command_preview="media-manager workflow run trip --label Italy_2025",
    )
    right = WorkflowProfileBundleItem(
        name="trip",
        title="Italy trip",
        workflow_name="trip",
        preset_name="trip-hardlink-collection",
        profile_name="Italy trip",
        profile_path="right/trip.json",
        relative_profile_path="trip.json",
        valid=False,
        problems=("Missing required values: end",),
        command_preview=None,
    )

    from media_manager.core.workflows.profile_bundle import WorkflowProfileBundle, WorkflowProfileBundleSummary

    empty_summary = WorkflowProfileBundleSummary(profile_count=0, valid_count=0, invalid_count=0)
    comparison = compare_workflow_profile_bundles(
        WorkflowProfileBundle("left", None, None, False, False, empty_summary, [left]),
        WorkflowProfileBundle("right", None, None, False, False, empty_summary, [right]),
    )

    assert comparison.summary.changed_count == 1
    assert comparison.summary.changed_validity_count == 1
    assert comparison.entries[0].status == "changed"
    assert comparison.entries[0].validity_changed is True


def test_extract_workflow_profile_bundle_writes_profiles_with_relative_paths(tmp_path: Path) -> None:
    bundle_path = tmp_path / "exports" / "profiles-bundle.json"
    profiles_dir = tmp_path / "profiles"
    nested_dir = profiles_dir / "family"
    nested_dir.mkdir(parents=True)
    (nested_dir / "trip.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy trip",
                "preset": "trip-hardlink-collection",
                "values": {
                    "source": ["C:/Phone"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14",
                },
            }
        ),
        encoding="utf-8",
    )

    written = write_workflow_profile_bundle(bundle_path, profiles_dir)
    loaded = load_workflow_profile_bundle(written)
    target_dir = tmp_path / "materialized"

    result = extract_workflow_profile_bundle(loaded, target_dir)

    assert result.selected_count == 1
    assert result.written_count == 1
    assert (target_dir / "family" / "trip.json").exists()
    materialized = json.loads((target_dir / "family" / "trip.json").read_text(encoding="utf-8"))
    assert materialized["profile_name"] == "Italy trip"
    assert loaded.profiles[0].profile_payload is not None
    assert loaded.profiles[0].profile_payload["values"]["label"] == "Italy_2025"


def test_extract_workflow_profile_bundle_conflicts_without_overwrite_and_can_overwrite(tmp_path: Path) -> None:
    bundle_path = tmp_path / "exports" / "profiles-bundle.json"
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "trip.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy trip",
                "preset": "trip-hardlink-collection",
                "values": {
                    "source": ["C:/Phone"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14",
                },
            }
        ),
        encoding="utf-8",
    )
    loaded = load_workflow_profile_bundle(write_workflow_profile_bundle(bundle_path, profiles_dir))
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "trip.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Different trip",
                "preset": "trip-copy-review",
                "values": {
                    "source": ["C:/Phone"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14",
                },
            }
        ),
        encoding="utf-8",
    )

    first = extract_workflow_profile_bundle(loaded, target_dir, preserve_structure=False)
    assert first.conflict_count == 1
    assert first.written_count == 0

    second = extract_workflow_profile_bundle(loaded, target_dir, preserve_structure=False, overwrite=True)
    assert second.conflict_count == 0
    assert second.written_count == 1
    materialized = json.loads((target_dir / "trip.json").read_text(encoding="utf-8"))
    assert materialized["preset"] == "trip-hardlink-collection"



def test_sync_workflow_profile_bundle_previews_write_and_delete(tmp_path: Path) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "trip.json").write_text(
        "\n".join([
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
        ]),
        encoding="utf-8",
    )
    bundle = build_workflow_profile_bundle(profiles_dir)
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "obsolete.json").write_text("{}", encoding="utf-8")

    result = sync_workflow_profile_bundle(bundle, target_dir, prune=True, apply=False)

    assert result.selected_count == 1
    assert result.planned_write_count == 1
    assert result.planned_delete_count == 1
    assert result.written_count == 0
    assert result.deleted_count == 0
    assert (target_dir / "trip.json").exists() is False


def test_sync_workflow_profile_bundle_applies_overwrite_and_prune(tmp_path: Path) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "trip.json").write_text(
        "\n".join([
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
        ]),
        encoding="utf-8",
    )
    bundle = build_workflow_profile_bundle(profiles_dir)
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "trip.json").write_text('{"different": true}', encoding="utf-8")
    (target_dir / "obsolete.json").write_text("{}", encoding="utf-8")

    result = sync_workflow_profile_bundle(bundle, target_dir, overwrite=True, prune=True, apply=True)

    assert result.overwritten_count == 1
    assert result.deleted_count == 1
    payload = json.loads((target_dir / "trip.json").read_text(encoding="utf-8"))
    assert payload["preset"] == "trip-hardlink-collection"
    assert not (target_dir / "obsolete.json").exists()
