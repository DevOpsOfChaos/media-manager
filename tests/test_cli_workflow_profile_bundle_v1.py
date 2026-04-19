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


def _write_invalid_trip_profile(path: Path) -> None:
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
                    "start": "2025-08-01"
                },
            }
        ),
        encoding="utf-8",
    )


def test_cli_workflow_profile_bundle_merge_prefers_last(tmp_path: Path, capsys) -> None:
    left_profiles = tmp_path / "left_profiles"
    right_profiles = tmp_path / "right_profiles"
    left_profiles.mkdir()
    right_profiles.mkdir()
    _write_valid_trip_profile(left_profiles / "trip.json")
    (right_profiles / "trip.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy trip copy",
                "preset": "trip-copy-review",
                "values": {
                    "source": ["C:/Phone"],
                    "target": "E:/Trips",
                    "label": "Italy_2025",
                    "start": "2025-08-01",
                    "end": "2025-08-14"
                },
            }
        ),
        encoding="utf-8",
    )
    left_bundle = tmp_path / "left.json"
    right_bundle = tmp_path / "right.json"
    merged_bundle = tmp_path / "merged.json"

    main(["profile-bundle-write", str(left_bundle), "--profiles-dir", str(left_profiles)])
    _ = capsys.readouterr()
    main(["profile-bundle-write", str(right_bundle), "--profiles-dir", str(right_profiles)])
    _ = capsys.readouterr()

    exit_code = main([
        "profile-bundle-merge",
        str(merged_bundle),
        str(left_bundle),
        str(right_bundle),
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["profile_count"] == 1
    assert payload["profiles"][0]["preset_name"] == "trip-copy-review"


def test_cli_workflow_profile_bundle_compare_detects_changed_profiles(tmp_path: Path, capsys) -> None:
    left_profiles = tmp_path / "left_profiles"
    right_profiles = tmp_path / "right_profiles"
    left_profiles.mkdir()
    right_profiles.mkdir()
    _write_valid_trip_profile(left_profiles / "trip.json")
    _write_invalid_trip_profile(right_profiles / "trip.json")
    left_bundle = tmp_path / "left.json"
    right_bundle = tmp_path / "right.json"

    main(["profile-bundle-write", str(left_bundle), "--profiles-dir", str(left_profiles)])
    _ = capsys.readouterr()
    main(["profile-bundle-write", str(right_bundle), "--profiles-dir", str(right_profiles)])
    _ = capsys.readouterr()

    exit_code = main([
        "profile-bundle-compare",
        str(left_bundle),
        str(right_bundle),
        "--only-changed",
        "--fail-on-changes",
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["summary"]["changed_count"] == 1
    assert payload["summary"]["changed_validity_count"] == 1
    assert payload["entries"][0]["status"] == "changed"


def test_cli_workflow_profile_bundle_extract_writes_matching_profiles(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    nested_dir = profiles_dir / "family"
    nested_dir.mkdir(parents=True)
    _write_valid_trip_profile(nested_dir / "trip.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"
    target_dir = tmp_path / "materialized"

    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    exit_code = main([
        "profile-bundle-extract",
        str(bundle_path),
        "--target-dir",
        str(target_dir),
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["written_count"] == 1
    assert (target_dir / "family" / "trip.json").exists()


def test_cli_workflow_profile_bundle_extract_reports_conflict_and_overwrite(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"
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

    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    first_code = main([
        "profile-bundle-extract",
        str(bundle_path),
        "--target-dir",
        str(target_dir),
        "--flatten",
        "--json",
    ])
    first = capsys.readouterr()
    assert first_code == 1
    first_payload = json.loads(first.out)
    assert first_payload["conflict_count"] == 1

    second_code = main([
        "profile-bundle-extract",
        str(bundle_path),
        "--target-dir",
        str(target_dir),
        "--flatten",
        "--overwrite",
        "--json",
    ])
    second = capsys.readouterr()
    assert second_code == 0
    second_payload = json.loads(second.out)
    assert second_payload["written_count"] == 1
    written = json.loads((target_dir / "trip.json").read_text(encoding="utf-8"))
    assert written["preset"] == "trip-hardlink-collection"



def test_cli_workflow_profile_bundle_sync_preview_and_apply(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "obsolete.json").write_text("{}", encoding="utf-8")

    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    preview_code = main([
        "profile-bundle-sync",
        str(bundle_path),
        "--target-dir",
        str(target_dir),
        "--prune",
        "--json",
    ])
    preview_captured = capsys.readouterr()

    assert preview_code == 0
    preview_payload = json.loads(preview_captured.out)
    assert preview_payload["planned_write_count"] == 1
    assert preview_payload["planned_delete_count"] == 1
    assert not (target_dir / "trip.json").exists()

    apply_code = main([
        "profile-bundle-sync",
        str(bundle_path),
        "--target-dir",
        str(target_dir),
        "--prune",
        "--apply",
        "--json",
    ])
    apply_captured = capsys.readouterr()

    assert apply_code == 0
    apply_payload = json.loads(apply_captured.out)
    assert apply_payload["written_count"] == 1
    assert apply_payload["deleted_count"] == 1
    assert (target_dir / "trip.json").exists()
    assert not (target_dir / "obsolete.json").exists()


def test_cli_workflow_profile_bundle_sync_reports_conflict(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "trip.json").write_text('{"different": true}', encoding="utf-8")

    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    exit_code = main([
        "profile-bundle-sync",
        str(bundle_path),
        "--target-dir",
        str(target_dir),
        "--json",
    ])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["conflict_count"] == 1
    assert payload["entries"][0]["status"] == "conflict"



def test_cli_workflow_profile_bundle_run_executes_valid_profiles(tmp_path: Path, capsys, monkeypatch) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"

    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    from media_manager.cli_workflow import DELEGATE_HANDLERS

    captured_args: list[str] = []

    def fake_trip_handler(args: list[str]) -> int:
        captured_args.extend(args)
        print("trip-handler-called")
        return 0

    monkeypatch.setitem(DELEGATE_HANDLERS, "trip", fake_trip_handler)

    exit_code = main(["profile-bundle-run", str(bundle_path), "--show-command", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["selected_count"] == 1
    assert payload["summary"]["executed_count"] == 1
    assert payload["summary"]["succeeded_count"] == 1
    assert payload["runs"][0]["status"] == "ok"
    assert payload["runs"][0]["delegated"] is True
    assert "--label" in captured_args
    assert "--link" in captured_args



def test_cli_workflow_profile_bundle_run_blocks_invalid_profiles(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_invalid_duplicates_profile(profiles_dir / "bad.json")
    bundle_path = tmp_path / "bundles" / "profiles.json"

    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    exit_code = main(["profile-bundle-run", str(bundle_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["summary"]["blocked_count"] == 1
    assert payload["runs"][0]["status"] == "invalid"



def test_cli_workflow_profile_bundle_run_can_continue_on_error(tmp_path: Path, capsys, monkeypatch) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    _write_valid_trip_profile(profiles_dir / "trip-one.json")
    (profiles_dir / "trip-two.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Italy trip copy",
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
    bundle_path = tmp_path / "bundles" / "profiles.json"

    main(["profile-bundle-write", str(bundle_path), "--profiles-dir", str(profiles_dir)])
    _ = capsys.readouterr()

    from media_manager.cli_workflow import DELEGATE_HANDLERS

    call_count = {"count": 0}

    def fake_trip_handler(args: list[str]) -> int:
        call_count["count"] += 1
        print(f"trip-handler-{call_count['count']}")
        return 1 if call_count["count"] == 1 else 0

    monkeypatch.setitem(DELEGATE_HANDLERS, "trip", fake_trip_handler)

    exit_code = main(["profile-bundle-run", str(bundle_path), "--continue-on-error", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["summary"]["executed_count"] == 2
    assert payload["summary"]["succeeded_count"] == 1
    assert payload["summary"]["failed_count"] == 1
    assert payload["summary"]["stopped_after_error"] is False
    assert payload["summary"]["exit_code_summary"] == {"0": 1, "1": 1}
