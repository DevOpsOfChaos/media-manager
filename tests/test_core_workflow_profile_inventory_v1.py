from __future__ import annotations

import json
from pathlib import Path

from media_manager.core.workflows import (
    build_workflow_profile_inventory,
    scan_workflow_profile_inventory,
    summarize_workflow_profile_records,
)


def test_scan_workflow_profile_inventory_recursively_collects_valid_and_invalid_profiles(tmp_path: Path) -> None:
    profiles_dir = tmp_path / "profiles"
    nested = profiles_dir / "nested"
    nested.mkdir(parents=True)

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
    (nested / "bad-duplicates.json").write_text(
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

    records = scan_workflow_profile_inventory(profiles_dir)

    assert len(records) == 2
    assert any(item.profile_name == "Family cleanup" and item.valid for item in records)
    assert any(item.profile_name == "Bad duplicates" and not item.valid for item in records)

    summary = summarize_workflow_profile_records(records)
    assert summary["profile_count"] == 2
    assert summary["valid_count"] == 1
    assert summary["invalid_count"] == 1
    assert any("Similar review requires similar_images." in key for key in summary["problem_summary"])


def test_build_workflow_profile_inventory_can_filter_invalid_duplicates_profiles(tmp_path: Path) -> None:
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

    inventory = build_workflow_profile_inventory(
        profiles_dir,
        workflow_name="duplicates",
        only_invalid=True,
    )

    assert inventory.build_summary()["profile_count"] == 1
    assert inventory.records[0].profile_name == "Bad duplicates"
    assert inventory.records[0].workflow_name == "duplicates"
    assert inventory.records[0].valid is False
