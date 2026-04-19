from __future__ import annotations

import json
from pathlib import Path

import pytest

from media_manager.core.workflows.profile_inventory import (
    WorkflowProfileRecord,
    build_workflow_profile_inventory,
    filter_workflow_profile_records,
)
from media_manager.core.workflows.profile_bundle import (
    WorkflowProfileBundle,
    WorkflowProfileBundleItem,
    WorkflowProfileBundleSummary,
    build_workflow_profile_bundle,
    extract_workflow_profile_bundle,
    filter_workflow_profile_bundle,
    sync_workflow_profile_bundle,
)
from media_manager.core.workflows.profile_bundle_inventory import build_workflow_profile_bundle_inventory



def _record(name: str, title: str, profile_name: str | None, path: str, *, valid: bool = True) -> WorkflowProfileRecord:
    return WorkflowProfileRecord(
        name=name,
        title=title,
        workflow_name="cleanup",
        preset_name="cleanup-family-library",
        profile_name=profile_name,
        profile_path=Path(path),
        valid=valid,
        command_preview=f"run {name}",
    )



def _bundle_item(name: str, profile_name: str | None, rel_path: str, *, valid: bool = True) -> WorkflowProfileBundleItem:
    payload = {
        "profile_name": profile_name,
        "preset": "cleanup-family-library",
        "values": {"workflow": "cleanup", "token": name},
    }
    return WorkflowProfileBundleItem(
        name=name,
        title=profile_name or name,
        workflow_name="cleanup",
        preset_name="cleanup-family-library",
        profile_name=profile_name,
        profile_path=f"C:/profiles/{rel_path}",
        relative_profile_path=rel_path,
        valid=valid,
        command_preview=f"run {name}",
        profile_payload=payload,
    )



def _bundle(*items: WorkflowProfileBundleItem) -> WorkflowProfileBundle:
    summary = WorkflowProfileBundleSummary(
        profile_count=len(items),
        valid_count=sum(1 for item in items if item.valid),
        invalid_count=sum(1 for item in items if not item.valid),
        workflow_summary={"cleanup": len(items)} if items else {},
        preset_summary={"cleanup-family-library": len(items)} if items else {},
        problem_summary={},
        duplicate_profile_name_summary={},
        duplicate_command_summary={},
        duplicate_profile_name_count=0,
        duplicate_command_count=0,
    )
    return WorkflowProfileBundle(
        profiles_dir="profiles",
        workflow_filter=None,
        preset_filter=None,
        profile_name_filter=None,
        relative_path_filter=None,
        only_valid=False,
        only_invalid=False,
        summary=summary,
        profiles=list(items),
    )



def test_filter_workflow_profile_records_supports_profile_name_and_path_contains() -> None:
    records = [
        _record("family-cleanup", "Family Cleanup", "Family Library", "C:/profiles/family/cleanup.json"),
        _record("trip-italy", "Trip Italy", "Italy Trip", "C:/profiles/trips/italy.json"),
        _record("archive", "Archive", None, "C:/profiles/archive/archive.json"),
    ]

    by_name = filter_workflow_profile_records(records, profile_name_contains="trip")
    assert [item.name for item in by_name] == ["trip-italy"]

    by_fallback_name = filter_workflow_profile_records(records, profile_name_contains="archive")
    assert [item.name for item in by_fallback_name] == ["archive"]

    by_path = filter_workflow_profile_records(records, profile_path_contains="family/")
    assert [item.name for item in by_path] == ["family-cleanup"]

    by_windows_path = filter_workflow_profile_records(records, profile_path_contains="family\\")
    assert [item.name for item in by_windows_path] == ["family-cleanup"]



def test_build_workflow_profile_inventory_forwards_new_filters(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_scan(_profiles_dir: str | Path):
        return [_record("family-cleanup", "Family Cleanup", "Family Library", str(tmp_path / "family-cleanup.json"))]

    def fake_filter(records, **kwargs):
        captured.update(kwargs)
        return list(records)

    monkeypatch.setattr(
        "media_manager.core.workflows.profile_inventory.scan_workflow_profile_inventory",
        fake_scan,
    )
    monkeypatch.setattr(
        "media_manager.core.workflows.profile_inventory.filter_workflow_profile_records",
        fake_filter,
    )

    inventory = build_workflow_profile_inventory(
        tmp_path,
        workflow_name="cleanup",
        preset_name="cleanup-family-library",
        profile_name_contains="family",
        profile_path_contains="cleanup.json",
        only_valid=True,
    )

    assert inventory.records
    assert captured == {
        "workflow_name": "cleanup",
        "preset_name": "cleanup-family-library",
        "profile_name_contains": "family",
        "profile_path_contains": "cleanup.json",
        "only_valid": True,
        "only_invalid": False,
    }



def test_filter_workflow_profile_bundle_supports_profile_name_and_relative_path_contains() -> None:
    bundle = _bundle(
        _bundle_item("family-cleanup", "Family Library", "family/cleanup.json"),
        _bundle_item("trip-italy", "Italy Trip", "trips/italy.json"),
        _bundle_item("archive", None, "archive/archive.json"),
    )

    by_name = filter_workflow_profile_bundle(bundle, profile_name_contains="trip")
    assert [item.name for item in by_name.profiles] == ["trip-italy"]

    by_fallback_name = filter_workflow_profile_bundle(bundle, profile_name_contains="archive")
    assert [item.name for item in by_fallback_name.profiles] == ["archive"]

    by_relative_path = filter_workflow_profile_bundle(bundle, relative_path_contains="family/")
    assert [item.name for item in by_relative_path.profiles] == ["family-cleanup"]

    by_windows_relative_path = filter_workflow_profile_bundle(bundle, relative_path_contains="family\\")
    assert [item.name for item in by_windows_relative_path.profiles] == ["family-cleanup"]



def test_build_workflow_profile_bundle_forwards_new_filters(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}
    record = _record("family-cleanup", "Family Cleanup", "Family Library", str(tmp_path / "family" / "cleanup.json"))

    def fake_build_inventory(_profiles_dir: str | Path, **kwargs):
        captured.update(kwargs)
        return type("Inventory", (), {"records": [record]})()

    monkeypatch.setattr(
        "media_manager.core.workflows.profile_bundle.build_workflow_profile_inventory",
        fake_build_inventory,
    )
    monkeypatch.setattr(
        "media_manager.core.workflows.profile_bundle._load_profile_payload_from_path",
        lambda path: {"profile_name": "Family Library", "preset": "cleanup-family-library", "values": {"workflow": "cleanup"}},
    )

    bundle = build_workflow_profile_bundle(
        tmp_path,
        workflow_name="cleanup",
        preset_name="cleanup-family-library",
        profile_name_contains="family",
        profile_path_contains="family/cleanup.json",
        only_valid=True,
    )

    assert [item.name for item in bundle.profiles] == ["family-cleanup"]
    assert captured == {
        "workflow_name": "cleanup",
        "preset_name": "cleanup-family-library",
        "profile_name_contains": "family",
        "profile_path_contains": "family/cleanup.json",
        "only_valid": True,
        "only_invalid": False,
    }



def test_extract_workflow_profile_bundle_respects_selection_filters(tmp_path: Path) -> None:
    bundle = _bundle(
        _bundle_item("family-cleanup", "Family Library", "family/cleanup.json"),
        _bundle_item("trip-italy", "Italy Trip", "trips/italy.json"),
    )

    result = extract_workflow_profile_bundle(
        bundle,
        tmp_path / "out",
        profile_name_contains="trip",
    )

    assert result.selected_count == 1
    assert result.written_count == 1
    assert (tmp_path / "out" / "trips" / "italy.json").exists()
    assert not (tmp_path / "out" / "family" / "cleanup.json").exists()



def test_sync_workflow_profile_bundle_respects_relative_path_filter_and_prune(tmp_path: Path) -> None:
    target_dir = tmp_path / "profiles"
    target_dir.mkdir(parents=True, exist_ok=True)
    untouched = target_dir / "family" / "cleanup.json"
    untouched.parent.mkdir(parents=True, exist_ok=True)
    untouched.write_text(json.dumps({"profile_name": "Family Library", "preset": "cleanup-family-library", "values": {"workflow": "cleanup"}}), encoding="utf-8")

    bundle = _bundle(
        _bundle_item("family-cleanup", "Family Library", "family/cleanup.json"),
        _bundle_item("trip-italy", "Italy Trip", "trips/italy.json"),
    )

    result = sync_workflow_profile_bundle(
        bundle,
        target_dir,
        relative_path_contains="trips/",
        prune=True,
        apply=False,
    )

    assert result.selected_count == 1
    statuses = {item.relative_profile_path: item.status for item in result.entries}
    assert statuses["trips/italy.json"] == "planned-write"
    assert statuses["family/cleanup.json"] == "planned-delete"



def test_build_workflow_profile_bundle_inventory_applies_nested_profile_filters(tmp_path: Path) -> None:
    bundles_dir = tmp_path / "bundles"
    bundles_dir.mkdir(parents=True, exist_ok=True)

    first = _bundle(
        _bundle_item("family-cleanup", "Family Library", "family/cleanup.json"),
        _bundle_item("trip-italy", "Italy Trip", "trips/italy.json"),
    )
    second = _bundle(
        _bundle_item("archive", "Archive", "archive/archive.json"),
    )

    (bundles_dir / "first.json").write_text(json.dumps(first.to_dict(), indent=2), encoding="utf-8")
    (bundles_dir / "second.json").write_text(json.dumps(second.to_dict(), indent=2), encoding="utf-8")

    inventory = build_workflow_profile_bundle_inventory(
        bundles_dir,
        profile_name_contains="trip",
        relative_path_contains="trips/",
    )

    by_name = {item.bundle_name: item.profile_count for item in inventory.records}
    assert by_name == {"first": 1, "second": 0}


def test_write_and_load_bundle_preserve_new_filter_metadata(tmp_path: Path) -> None:
    from media_manager.core.workflows.presets import build_workflow_profile_payload
    from media_manager.core.workflows.profile_bundle import load_workflow_profile_bundle, write_workflow_profile_bundle

    profiles_dir = tmp_path / "profiles"
    family_dir = profiles_dir / "family"
    family_dir.mkdir(parents=True, exist_ok=True)
    (family_dir / "cleanup.json").write_text(
        json.dumps(
            build_workflow_profile_payload(
                profile_name="Family Library",
                preset_name="cleanup-family-library",
                values={
                    "source": ["C:/Photos"],
                    "target": "C:/Library",
                },
            )
        ),
        encoding="utf-8",
    )

    bundle_path = tmp_path / "bundle.json"
    write_workflow_profile_bundle(
        bundle_path,
        profiles_dir,
        profile_name_contains="family",
        profile_path_contains="family/",
    )

    loaded = load_workflow_profile_bundle(bundle_path)
    assert loaded.profile_name_filter == "family"
    assert loaded.relative_path_filter == "family/"
    assert [item.relative_profile_path for item in loaded.profiles] == ["family/cleanup.json"]
