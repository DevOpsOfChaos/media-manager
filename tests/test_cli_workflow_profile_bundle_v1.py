from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main


def _write_valid_trip_profile(path: Path) -> None:
    path.write_text(
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


def _write_invalid_duplicates_profile(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Bad duplicates",
                "preset": "duplicates-similar-review",
                "values": {
                    "source": ["C:/Photos"],
                    "show_similar_review": True,
                    "similar_images": False,
                },
            }
        ),
        encoding="utf-8",
    )


def test_cli_workflow_profile_bundle_write_and_show_json(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"

    write_code = main([
        "profile-bundle-write",
        str(bundle_path),
        "--profiles-dir",
        str(profiles_dir),
        "--json",
    ])
    write_captured = capsys.readouterr()

    assert write_code == 0
    write_payload = json.loads(write_captured.out)
    assert write_payload["output_path"] == str(bundle_path)
    assert write_payload["summary"]["profile_count"] == 1
    assert bundle_path.exists()

    show_code = main(["profile-bundle-show", str(bundle_path), "--json"])
    show_captured = capsys.readouterr()

    assert show_code == 0
    show_payload = json.loads(show_captured.out)
    assert show_payload["summary"]["valid_count"] == 1
    assert show_payload["profiles"][0]["relative_profile_path"] == "trip.json"


def test_cli_workflow_profile_bundle_show_can_filter_invalid_profiles(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    _write_invalid_duplicates_profile(profiles_dir / "bad.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"
    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    exit_code = main(["profile-bundle-show", str(bundle_path), "--only-invalid", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["profile_count"] == 1
    assert payload["profiles"][0]["profile_name"] == "Bad duplicates"


def test_cli_workflow_profile_bundle_audit_returns_error_for_invalid_profiles(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    _write_invalid_duplicates_profile(profiles_dir / "bad.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"
    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    exit_code = main(["profile-bundle-audit", str(bundle_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["summary"]["invalid_count"] == 1


def test_cli_workflow_profile_bundle_audit_can_fail_on_empty(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"
    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    exit_code = main([
        "profile-bundle-audit",
        str(bundle_path),
        "--workflow",
        "duplicates",
        "--fail-on-empty",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["summary"]["profile_count"] == 0
