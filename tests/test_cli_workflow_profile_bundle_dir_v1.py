from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main


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


def test_cli_workflow_profile_bundle_list_dir_json_counts_clean_and_problematic(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / 'profiles'
    profiles_dir.mkdir()
    _write_trip_profile(profiles_dir / 'trip.json')
    bundles_dir = tmp_path / 'bundles'
    bundles_dir.mkdir()
    main(['profile-bundle-write', str(bundles_dir / 'valid.json'), '--profiles-dir', str(profiles_dir)])
    _ = capsys.readouterr()
    (bundles_dir / 'broken.json').write_text('{not-json', encoding='utf-8')

    exit_code = main(['profile-bundle-list-dir', '--bundles-dir', str(bundles_dir), '--json'])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload['summary']['bundle_count'] == 2
    assert payload['summary']['clean_bundle_count'] == 1
    assert payload['summary']['problematic_bundle_count'] == 1


def test_cli_workflow_profile_bundle_audit_dir_returns_error_for_problematic_bundle(tmp_path: Path, capsys) -> None:
    bundles_dir = tmp_path / 'bundles'
    bundles_dir.mkdir()
    (bundles_dir / 'broken.json').write_text('{not-json', encoding='utf-8')

    exit_code = main(['profile-bundle-audit-dir', '--bundles-dir', str(bundles_dir), '--json'])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload['summary']['problematic_bundle_count'] == 1


def test_cli_workflow_profile_bundle_run_dir_executes_profiles_from_multiple_bundles(tmp_path: Path, capsys, monkeypatch) -> None:
    left_profiles = tmp_path / 'left_profiles'
    right_profiles = tmp_path / 'right_profiles'
    left_profiles.mkdir()
    right_profiles.mkdir()
    _write_trip_profile(left_profiles / 'trip-one.json')
    _write_trip_profile(right_profiles / 'trip-two.json')
    bundles_dir = tmp_path / 'bundles'
    bundles_dir.mkdir()
    main(['profile-bundle-write', str(bundles_dir / 'one.json'), '--profiles-dir', str(left_profiles)])
    _ = capsys.readouterr()
    main(['profile-bundle-write', str(bundles_dir / 'two.json'), '--profiles-dir', str(right_profiles)])
    _ = capsys.readouterr()

    from media_manager.cli_workflow import DELEGATE_HANDLERS
    calls: list[list[str]] = []

    def fake_trip_handler(args: list[str]) -> int:
        calls.append(list(args))
        print('trip-handler-called')
        return 0

    monkeypatch.setitem(DELEGATE_HANDLERS, 'trip', fake_trip_handler)

    exit_code = main(['profile-bundle-run-dir', '--bundles-dir', str(bundles_dir), '--json'])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload['summary']['selected_bundle_count'] == 2
    assert payload['summary']['selected_profile_count'] == 2
    assert payload['summary']['executed_count'] == 2
    assert payload['summary']['succeeded_count'] == 2
    assert len(calls) == 2
