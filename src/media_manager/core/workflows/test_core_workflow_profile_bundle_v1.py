from __future__ import annotations

from pathlib import Path

from media_manager.core.workflows.profile_bundle import (
    WorkflowProfileBundleItem,
    build_workflow_profile_bundle_items,
    build_workflow_profile_bundle_summary,
    load_workflow_profile_bundle,
    write_workflow_profile_bundle,
)
from media_manager.core.workflows.profile_inventory import WorkflowProfileRecord


def test_build_workflow_profile_bundle_items_adds_relative_paths(tmp_path: Path) -> None:
    profiles_dir = tmp_path / 'profiles'
    nested = profiles_dir / 'family'
    nested.mkdir(parents=True)
    profile_path = nested / 'cleanup.json'

    records = [
        WorkflowProfileRecord(
            name='cleanup',
            title='Family cleanup',
            workflow_name='cleanup',
            preset_name='cleanup-family-library',
            profile_name='Family cleanup',
            profile_path=profile_path,
            valid=True,
            missing_required_fields=(),
            problems=(),
            command_preview='media-manager workflow run cleanup --source C:/Photos --target E:/Library',
        )
    ]

    items = build_workflow_profile_bundle_items(records, profiles_dir=profiles_dir)

    assert len(items) == 1
    assert items[0].relative_profile_path == 'family/cleanup.json'
    assert items[0].profile_path.endswith('cleanup.json')


def test_build_workflow_profile_bundle_summary_counts_duplicates() -> None:
    items = [
        WorkflowProfileBundleItem(
            name='one',
            title='Family cleanup',
            workflow_name='cleanup',
            preset_name='cleanup-family-library',
            profile_name='Family cleanup',
            profile_path='profiles/one.json',
            relative_profile_path='one.json',
            valid=True,
            command_preview='media-manager workflow run cleanup --source C:/Photos --target E:/Library',
        ),
        WorkflowProfileBundleItem(
            name='two',
            title='Family cleanup',
            workflow_name='cleanup',
            preset_name='cleanup-family-library',
            profile_name='Family cleanup',
            profile_path='profiles/two.json',
            relative_profile_path='two.json',
            valid=True,
            command_preview='media-manager workflow run cleanup --source C:/Photos --target E:/Library',
        ),
        WorkflowProfileBundleItem(
            name='bad',
            title='Bad duplicates',
            workflow_name='duplicates',
            preset_name='duplicates-similar-review',
            profile_name='Bad duplicates',
            profile_path='profiles/bad.json',
            relative_profile_path='bad.json',
            valid=False,
            problems=('duplicates apply requires yes',),
            command_preview=None,
        ),
    ]

    summary = build_workflow_profile_bundle_summary(items)

    assert summary.profile_count == 3
    assert summary.valid_count == 2
    assert summary.invalid_count == 1
    assert summary.workflow_summary['cleanup'] == 2
    assert summary.preset_summary['cleanup-family-library'] == 2
    assert summary.problem_summary['duplicates apply requires yes'] == 1
    assert summary.duplicate_profile_name_summary['Family cleanup'] == 2
    assert summary.duplicate_profile_name_count == 2
    assert summary.duplicate_command_count == 2


def test_write_and_load_workflow_profile_bundle_roundtrip(tmp_path: Path) -> None:
    bundle_path = tmp_path / 'exports' / 'profiles-bundle.json'
    profiles_dir = tmp_path / 'profiles'
    profiles_dir.mkdir()
    (profiles_dir / 'trip.json').write_text(
        '
'.join([
            '{',
            '  "schema_version": 1,',
            '  "profile_name": "Italy trip",',
            '  "preset": "trip-hardlink-collection",',
            '  "values": {',
            '    "source": ["C:/Phone"],',
            '    "target": "E:/Trips",',
            '    "label": "Italy_2025",',
            '    "start": "2025-08-01",',
            '    "end": "2025-08-14"',
            '  }',
            '}',
        ]),
        encoding='utf-8',
    )

    written = write_workflow_profile_bundle(bundle_path, profiles_dir)
    loaded = load_workflow_profile_bundle(written)

    assert written.exists()
    assert loaded.summary.profile_count == 1
    assert loaded.summary.valid_count == 1
    assert loaded.profiles[0].profile_name == 'Italy trip'
    assert loaded.profiles[0].relative_profile_path == 'trip.json'
