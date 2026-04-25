from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import main
from media_manager.core.workflows.presets import build_workflow_profile_payload


def _write_profile(
    path: Path,
    *,
    profile_name: str,
    preset_name: str,
    values: dict[str, object],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_workflow_profile_payload(
        profile_name=profile_name,
        preset_name=preset_name,
        values=values,
    )
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def test_profile_list_json_filters_by_profile_name_contains(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    _write_profile(
        profiles_dir / "family" / "cleanup.json",
        profile_name="Family Cleanup",
        preset_name="cleanup-family-library",
        values={
            "source": ["C:/Photos"],
            "target": "E:/Library",
        },
    )
    _write_profile(
        profiles_dir / "trips" / "italy.json",
        profile_name="Italy Trip",
        preset_name="trip-hardlink-collection",
        values={
            "source": ["C:/Phone"],
            "target": "E:/Trips",
            "label": "Italy_2025",
            "start": "2025-08-01",
            "end": "2025-08-14",
        },
    )

    exit_code = main([
        "profile-list",
        "--profiles-dir",
        str(profiles_dir),
        "--profile-name-contains",
        "trip",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["profile_name_contains"] == "trip"
    assert payload["summary"]["profile_count"] == 1
    assert [item["profile_name"] for item in payload["profiles"]] == ["Italy Trip"]



def test_profile_list_json_filters_by_profile_path_contains_with_backslash(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    _write_profile(
        profiles_dir / "family" / "cleanup.json",
        profile_name="Family Cleanup",
        preset_name="cleanup-family-library",
        values={
            "source": ["C:/Photos"],
            "target": "E:/Library",
        },
    )
    _write_profile(
        profiles_dir / "misc" / "cleanup.json",
        profile_name="Misc Cleanup",
        preset_name="cleanup-family-library",
        values={
            "source": ["D:/Photos"],
            "target": "E:/Library",
        },
    )

    exit_code = main([
        "profile-list",
        "--profiles-dir",
        str(profiles_dir),
        "--profile-path-contains",
        "family\\",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["profile_path_contains"] == "family\\"
    assert payload["summary"]["profile_count"] == 1
    assert [Path(item["profile_path"]).name for item in payload["profiles"]] == ["cleanup.json"]
    assert payload["profiles"][0]["profile_name"] == "Family Cleanup"



def test_profile_bundle_write_json_preserves_selection_metadata(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    _write_profile(
        profiles_dir / "family" / "cleanup.json",
        profile_name="Family Cleanup",
        preset_name="cleanup-family-library",
        values={
            "source": ["C:/Photos"],
            "target": "E:/Library",
        },
    )
    _write_profile(
        profiles_dir / "trips" / "italy.json",
        profile_name="Italy Trip",
        preset_name="trip-hardlink-collection",
        values={
            "source": ["C:/Phone"],
            "target": "E:/Trips",
            "label": "Italy_2025",
            "start": "2025-08-01",
            "end": "2025-08-14",
        },
    )
    bundle_path = tmp_path / "bundle.json"

    exit_code = main([
        "profile-bundle-write",
        str(bundle_path),
        "--profiles-dir",
        str(profiles_dir),
        "--profile-name-contains",
        "family",
        "--profile-path-contains",
        "family/",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["output_path"] == str(bundle_path)
    assert payload["profile_name_contains"] == "family"
    assert payload["relative_path_contains"] == "family/"
    assert payload["summary"]["profile_count"] == 1
    assert [item["relative_profile_path"] for item in payload["profiles"]] == ["family/cleanup.json"]



def test_profile_bundle_show_json_filters_by_relative_path_contains(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    _write_profile(
        profiles_dir / "family" / "cleanup.json",
        profile_name="Family Cleanup",
        preset_name="cleanup-family-library",
        values={
            "source": ["C:/Photos"],
            "target": "E:/Library",
        },
    )
    _write_profile(
        profiles_dir / "trips" / "italy.json",
        profile_name="Italy Trip",
        preset_name="trip-hardlink-collection",
        values={
            "source": ["C:/Phone"],
            "target": "E:/Trips",
            "label": "Italy_2025",
            "start": "2025-08-01",
            "end": "2025-08-14",
        },
    )
    bundle_path = tmp_path / "bundle.json"
    write_exit_code = main([
        "profile-bundle-write",
        str(bundle_path),
        "--profiles-dir",
        str(profiles_dir),
    ])
    _ = capsys.readouterr()
    assert write_exit_code == 0

    exit_code = main([
        "profile-bundle-show",
        str(bundle_path),
        "--relative-path-contains",
        "trips\\",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["relative_path_contains"] == "trips\\"
    assert payload["summary"]["profile_count"] == 1
    assert [item["profile_name"] for item in payload["profiles"]] == ["Italy Trip"]



def test_profile_bundle_list_dir_json_filters_by_profile_name_contains(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    _write_profile(
        profiles_dir / "family" / "cleanup.json",
        profile_name="Family Cleanup",
        preset_name="cleanup-family-library",
        values={
            "source": ["C:/Photos"],
            "target": "E:/Library",
        },
    )
    _write_profile(
        profiles_dir / "trips" / "italy.json",
        profile_name="Italy Trip",
        preset_name="trip-hardlink-collection",
        values={
            "source": ["C:/Phone"],
            "target": "E:/Trips",
            "label": "Italy_2025",
            "start": "2025-08-01",
            "end": "2025-08-14",
        },
    )
    bundles_dir = tmp_path / "bundles"
    first_bundle = bundles_dir / "mixed.json"
    second_bundle = bundles_dir / "family-only.json"

    exit_code = main([
        "profile-bundle-write",
        str(first_bundle),
        "--profiles-dir",
        str(profiles_dir),
    ])
    _ = capsys.readouterr()
    assert exit_code == 0

    exit_code = main([
        "profile-bundle-write",
        str(second_bundle),
        "--profiles-dir",
        str(profiles_dir),
        "--profile-name-contains",
        "family",
    ])
    _ = capsys.readouterr()
    assert exit_code == 0

    exit_code = main([
        "profile-bundle-list-dir",
        "--bundles-dir",
        str(bundles_dir),
        "--profile-name-contains",
        "family",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["profile_name_contains"] == "family"
    assert payload["summary"]["bundle_count"] == 2
    assert all(item["profile_count"] == 1 for item in payload["bundles"])
