from __future__ import annotations

import json
from pathlib import Path

from media_manager.cleanup_plan import build_exact_cleanup_dry_run, build_exact_group_id
from media_manager.duplicate_workflow import build_duplicate_workflow_bundle
from media_manager.duplicates import DuplicateScanConfig, ExactDuplicateGroup, scan_exact_duplicates
from media_manager.execution_audit import (
    build_duplicate_execution_audit_payload,
    write_duplicate_execution_audit_log,
)
from media_manager.execution_runner import run_duplicate_execution_preview



def _group(paths: list[Path], file_size: int = 1234, digest: str = "digest") -> ExactDuplicateGroup:
    return ExactDuplicateGroup(
        files=paths,
        file_size=file_size,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )



def test_build_duplicate_execution_audit_payload_for_preview_only(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "one.jpg"
    second = source / "two.jpg"
    first.write_bytes(b"duplicate-bytes")
    second.write_bytes(b"duplicate-bytes")

    scan_result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))
    decisions = {build_exact_group_id(scan_result.exact_groups[0]): str(first)}
    bundle = build_duplicate_workflow_bundle(scan_result.exact_groups, decisions, "delete")

    payload = build_duplicate_execution_audit_payload(
        scan_result,
        bundle,
        None,
        apply_requested=False,
    )

    assert payload["schema_version"] == 1
    assert payload["apply_requested"] is False
    assert payload["scan"]["exact_groups"] == 1
    assert payload["decisions_count"] == 1
    assert payload["execution_run"] is None



def test_write_duplicate_execution_audit_log_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "one.jpg"
    second = source / "two.jpg"
    first.write_bytes(b"duplicate-bytes")
    second.write_bytes(b"duplicate-bytes")

    scan_result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))
    decisions = {build_exact_group_id(scan_result.exact_groups[0]): str(first)}
    bundle = build_duplicate_workflow_bundle(scan_result.exact_groups, decisions, "delete")
    execution_result = run_duplicate_execution_preview(bundle.execution_preview, apply=False)

    audit_path = tmp_path / "audit" / "duplicate-audit.json"
    written_path = write_duplicate_execution_audit_log(
        audit_path,
        scan_result,
        bundle,
        execution_result,
        apply_requested=False,
    )

    assert written_path == audit_path
    assert audit_path.exists()

    payload = json.loads(audit_path.read_text(encoding="utf-8"))
    assert payload["apply_requested"] is False
    assert payload["execution_run"]["processed_rows"] == 1
    assert payload["execution_run"]["entries"][0]["outcome"] == "preview-trash"
