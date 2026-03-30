from __future__ import annotations

from pathlib import Path

from media_manager.cleanup_plan import build_exact_cleanup_dry_run, build_exact_group_id
from media_manager.duplicate_workflow import build_duplicate_workflow_bundle
from media_manager.duplicates import ExactDuplicateGroup
from media_manager.execution_runner import run_duplicate_execution_preview
from media_manager.execution_safety import find_associated_sibling_paths, protect_duplicate_execution_preview



def _group(paths: list[Path], file_size: int = 1234, digest: str = "digest") -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=paths,
        file_size=file_size,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )



def test_find_associated_sibling_paths_returns_same_stem_peers(tmp_path: Path) -> None:
    media = tmp_path / "IMG_0001.JPG"
    sidecar = tmp_path / "IMG_0001.XMP"
    audio = tmp_path / "IMG_0001.WAV"
    other = tmp_path / "IMG_0002.JPG"
    media.write_bytes(b"jpg")
    sidecar.write_bytes(b"xmp")
    audio.write_bytes(b"wav")
    other.write_bytes(b"other")

    related = find_associated_sibling_paths(media)

    assert related == [audio, sidecar]



def test_protect_duplicate_execution_preview_blocks_delete_when_sidecars_exist(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "IMG_0001.JPG"
    sidecar = tmp_path / "IMG_0001.XMP"
    keep.write_bytes(b"same")
    remove.write_bytes(b"same")
    sidecar.write_bytes(b"xmp")

    group = _group([keep, remove], file_size=4, digest="guarded")
    decisions = {build_exact_group_id(group): str(keep)}
    dry_run = build_exact_cleanup_dry_run([group], decisions, "delete")
    from media_manager.execution_plan import build_duplicate_execution_preview
    preview = build_duplicate_execution_preview(dry_run)

    guarded = protect_duplicate_execution_preview(preview)

    assert guarded.ready is False
    assert guarded.blocked_count == 1
    assert guarded.executable_count == 0
    assert guarded.rows[0].row_type == "blocked_associated_files"
    assert guarded.rows[0].reason == "associated_files_present"



def test_duplicate_workflow_bundle_blocks_execution_preview_when_associated_files_exist(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "IMG_0001.JPG"
    sidecar = tmp_path / "IMG_0001.XMP"
    keep.write_bytes(b"same")
    remove.write_bytes(b"same")
    sidecar.write_bytes(b"xmp")

    group = _group([keep, remove], file_size=4, digest="workflow-guard")
    decisions = {build_exact_group_id(group): str(keep)}

    bundle = build_duplicate_workflow_bundle([group], decisions, "delete")

    assert bundle.execution_preview.ready is False
    assert bundle.execution_preview.blocked_count == 1
    assert bundle.execution_preview.rows[0].reason == "associated_files_present"



def test_execution_runner_blocks_delete_when_associated_files_exist_even_if_preview_is_unsafe(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    remove = tmp_path / "IMG_0001.JPG"
    sidecar = tmp_path / "IMG_0001.XMP"
    keep.write_bytes(b"same")
    remove.write_bytes(b"same")
    sidecar.write_bytes(b"xmp")

    group = _group([keep, remove], file_size=4, digest="runner-guard")
    decisions = {build_exact_group_id(group): str(keep)}
    dry_run = build_exact_cleanup_dry_run([group], decisions, "delete")
    from media_manager.execution_plan import build_duplicate_execution_preview
    preview = build_duplicate_execution_preview(dry_run)
    result = run_duplicate_execution_preview(preview, apply=True)

    assert result.executed_rows == 0
    assert result.blocked_rows == 1
    assert result.error_rows == 0
    assert result.entries[0].reason == "associated_files_present"
    assert remove.exists()
