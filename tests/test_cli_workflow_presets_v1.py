from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_workflow import DELEGATE_HANDLERS, main


def test_cli_workflow_presets_json_lists_builtin_presets(capsys) -> None:
    exit_code = main(["presets", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert any(item["name"] == "cleanup-family-library" for item in payload["presets"])


def test_cli_workflow_presets_json_lists_new_review_presets(capsys) -> None:
    exit_code = main(["presets", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    names = {item["name"] for item in payload["presets"]}
    assert "duplicates-similar-review" in names
    assert "trip-copy-review" in names
    assert "organize-review-json" in names
    assert "rename-review-json" in names


def test_cli_workflow_render_preset_outputs_command(capsys) -> None:
    exit_code = main(
        [
            "render-preset",
            "cleanup-family-library",
            "--source",
            "C:/Photos",
            "--source",
            "D:/Phone",
            "--target",
            "E:/Library",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "media-manager workflow run cleanup" in captured.out
    assert "--target E:/Library" in captured.out


def test_cli_workflow_render_trip_copy_review_outputs_runtime_flags(capsys) -> None:
    exit_code = main(
        [
            "render-preset",
            "trip-copy-review",
            "--source",
            "C:/Phone",
            "--target",
            "E:/Trips",
            "--label",
            "Italy_2025",
            "--start",
            "2025-08-01",
            "--end",
            "2025-08-14",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "--copy" in captured.out
    assert "--show-files" in captured.out
    assert "--json" in captured.out


def test_cli_workflow_render_duplicates_similar_review_outputs_runtime_flags(capsys) -> None:
    exit_code = main(
        [
            "render-preset",
            "duplicates-similar-review",
            "--source",
            "C:/Library",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "--show-plan" in captured.out
    assert "--show-decisions" in captured.out
    assert "--similar-images" in captured.out
    assert "--show-similar-review" in captured.out


def test_cli_workflow_profile_show_reads_profile_json(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "cleanup-profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Family cleanup",
                "preset": "cleanup-family-library",
                "values": {
                    "source": ["C:/Photos", "D:/Phone"],
                    "target": "E:/Library",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["profile-show", str(profile_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["profile_name"] == "Family cleanup"
    assert payload["preset"] == "cleanup-family-library"
    assert payload["command"].startswith("media-manager workflow run cleanup")


def test_cli_workflow_profile_show_includes_runtime_flags_from_profile_json(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "rename-profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Rename review",
                "preset": "rename-review-json",
                "values": {
                    "source": ["C:/Photos"],
                    "history_dir": "runs",
                    "run_log": "logs/rename.json",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["profile-show", str(profile_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert "--show-files" in payload["command"]
    assert "--json" in payload["command"]
    assert "--history-dir runs" in payload["command"]
    assert "--run-log logs/rename.json" in payload["command"]


def test_cli_workflow_profile_save_writes_profile_json(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "profiles" / "trip-profile.json"

    exit_code = main(
        [
            "profile-save",
            str(profile_path),
            "--preset",
            "trip-hardlink-collection",
            "--profile-name",
            "Italy trip",
            "--source",
            "C:/Phone",
            "--target",
            "E:/Trips",
            "--label",
            "Italy_2025",
            "--start",
            "2025-08-01",
            "--end",
            "2025-08-14",
            "--json",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    written = json.loads(profile_path.read_text(encoding="utf-8"))
    assert payload["profile_name"] == "Italy trip"
    assert written["profile_name"] == "Italy trip"
    assert written["preset"] == "trip-hardlink-collection"


def test_cli_workflow_profile_validate_reports_valid_profile(tmp_path: Path, capsys) -> None:
    profile_path = tmp_path / "cleanup-profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Family cleanup",
                "preset": "cleanup-family-library",
                "values": {
                    "source": ["C:/Photos", "D:/Phone"],
                    "target": "E:/Library",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["profile-validate", str(profile_path), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["valid"] is True
    assert payload["workflow"] == "cleanup"
    assert payload["command"].startswith("media-manager workflow run cleanup")


def test_cli_workflow_profile_list_json_summarizes_profiles(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()

    (profiles_dir / "cleanup.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Family cleanup",
                "preset": "cleanup-family-library",
                "values": {
                    "source": ["C:/Photos", "D:/Phone"],
                    "target": "E:/Library",
                },
            }
        ),
        encoding="utf-8",
    )
    (profiles_dir / "bad-duplicates.json").write_text(
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

    exit_code = main(["profile-list", "--profiles-dir", str(profiles_dir), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["profile_count"] == 2
    assert payload["summary"]["valid_count"] == 1
    assert payload["summary"]["invalid_count"] == 1
    assert any(item["profile_name"] == "Family cleanup" for item in payload["profiles"])
    assert any(item["profile_name"] == "Bad duplicates" and item["valid"] is False for item in payload["profiles"])


def test_cli_workflow_profile_list_can_filter_invalid_only(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()

    (profiles_dir / "cleanup.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Family cleanup",
                "preset": "cleanup-family-library",
                "values": {
                    "source": ["C:/Photos", "D:/Phone"],
                    "target": "E:/Library",
                },
            }
        ),
        encoding="utf-8",
    )
    (profiles_dir / "bad-duplicates.json").write_text(
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

    exit_code = main(["profile-list", "--profiles-dir", str(profiles_dir), "--only-invalid", "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["profile_count"] == 1
    assert payload["summary"]["valid_count"] == 0
    assert payload["summary"]["invalid_count"] == 1
    assert [item["profile_name"] for item in payload["profiles"]] == ["Bad duplicates"]


def test_cli_workflow_profile_audit_returns_nonzero_for_invalid_profiles(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()

    (profiles_dir / "bad-duplicates.json").write_text(
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

    exit_code = main(["profile-audit", "--profiles-dir", str(profiles_dir), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["summary"]["profile_count"] == 1
    assert payload["summary"]["invalid_count"] == 1
    assert payload["profiles"][0]["profile_name"] == "Bad duplicates"
    assert payload["profiles"][0]["valid"] is False


def test_cli_workflow_profile_audit_returns_zero_for_valid_profiles(tmp_path: Path, capsys) -> None:
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()

    (profiles_dir / "cleanup.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Family cleanup",
                "preset": "cleanup-family-library",
                "values": {
                    "source": ["C:/Photos", "D:/Phone"],
                    "target": "E:/Library",
                },
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["profile-audit", "--profiles-dir", str(profiles_dir), "--json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["summary"]["profile_count"] == 1
    assert payload["summary"]["valid_count"] == 1
    assert payload["summary"]["invalid_count"] == 0


def test_cli_workflow_profile_run_delegates_to_trip_handler(tmp_path: Path, capsys, monkeypatch) -> None:
    profile_path = tmp_path / "trip-profile.json"
    profile_path.write_text(
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

    captured_args: list[str] = []

    def fake_trip_handler(args: list[str]) -> int:
        captured_args.extend(args)
        print("trip-handler-called")
        return 0

    monkeypatch.setitem(DELEGATE_HANDLERS, "trip", fake_trip_handler)

    exit_code = main(["profile-run", str(profile_path), "--show-command"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "media-manager workflow run trip" in captured.out
    assert "trip-handler-called" in captured.out
    assert "--source" in captured_args
    assert "--link" in captured_args


def test_cli_workflow_profile_run_delegates_runtime_flags_from_profile_json(tmp_path: Path, capsys, monkeypatch) -> None:
    profile_path = tmp_path / "duplicates-profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "profile_name": "Duplicates review",
                "preset": "duplicates-similar-review",
                "values": {
                    "source": ["C:/Library"],
                    "history_dir": "runs",
                },
            }
        ),
        encoding="utf-8",
    )

    captured_args: list[str] = []

    def fake_duplicates_handler(args: list[str]) -> int:
        captured_args.extend(args)
        print("duplicates-handler-called")
        return 0

    monkeypatch.setitem(DELEGATE_HANDLERS, "duplicates", fake_duplicates_handler)

    exit_code = main(["profile-run", str(profile_path), "--show-command"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "duplicates-handler-called" in captured.out
    assert "--show-decisions" in captured_args
    assert "--similar-images" in captured_args
    assert "--show-similar-review" in captured_args
    assert "--history-dir" in captured_args
