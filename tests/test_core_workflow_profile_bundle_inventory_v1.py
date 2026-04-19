from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows import build_workflow_profile_bundle_inventory, write_workflow_profile_bundle


def _write_trip_profile(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                'schema_version': 1,
                'profile_name': 'Italy trip',
                'preset': 'trip-hardlink-collection',
                'values': {
                    'source': ['C:/Phone'],
                    'target': 'E:/Trips',
                    'label': 'Italy_2025',
                    'start': '2025-08-01',
                    'end': '2025-08-14',
                },
            }
        ),
        encoding='utf-8',
    )


def test_build_workflow_profile_bundle_inventory_counts_clean_and_problematic_bundles(tmp_path: Path) -> None:
    profiles_dir = tmp_path / 'profiles'
    profiles_dir.mkdir()
    _write_trip_profile(profiles_dir / 'trip.json')
    bundles_dir = tmp_path / 'bundles'
    bundles_dir.mkdir()
    write_workflow_profile_bundle(bundles_dir / 'valid.json', profiles_dir)
    (bundles_dir / 'broken.json').write_text('{not-json', encoding='utf-8')

    inventory = build_workflow_profile_bundle_inventory(bundles_dir)
    summary = inventory.build_summary()

    assert summary['bundle_count'] == 2
    assert summary['clean_bundle_count'] == 1
    assert summary['problematic_bundle_count'] == 1
    assert summary['profile_count'] == 1
    assert summary['valid_count'] == 1


def test_build_workflow_profile_bundle_inventory_can_filter_problematic_bundle_name(tmp_path: Path) -> None:
    profiles_dir = tmp_path / 'profiles'
    profiles_dir.mkdir()
    _write_trip_profile(profiles_dir / 'trip.json')
    bundles_dir = tmp_path / 'bundles'
    bundles_dir.mkdir()
    write_workflow_profile_bundle(bundles_dir / 'valid.json', profiles_dir)
    (bundles_dir / 'broken.json').write_text('{not-json', encoding='utf-8')

    inventory = build_workflow_profile_bundle_inventory(
        bundles_dir,
        bundle_name='broken',
        only_problematic_bundles=True,
    )

    assert len(inventory.records) == 1
    assert inventory.records[0].bundle_name == 'broken'
    assert inventory.records[0].clean_bundle is False
