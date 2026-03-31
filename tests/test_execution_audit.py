from __future__ import annotations

import json
from pathlib import Path

from media_manager.cleanup_plan import build_exact_group_id
from media_manager.duplicate_workflow import build_duplicate_workflow_bundle
from media_manager.duplicates import DuplicateScanConfig, scan_exact_duplicates
from media_manager.execution_audit import (
    build_duplicate_execution_audit_payload,
    determine_duplicate_cli_exit_code,
    write_duplicate_execution_audit_log,
)
from media_manager.execution_runner import run_duplicate_execution_preview


def test_build_duplicate_execution_audit_payload_for_planning_only(tmp_path: Path) -> None:
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
    assert payload["execution_status"] == "planned_only"
    assert payload["recommended_exit_code"] == 0
    assert payload["scan"]["exact_groups"] == 1
    assert payload["decisions_count"] == 1
    assert payload["execution_run"] is None


def test_determine_duplicate_cli_exit_code_returns_incomplete_apply_code(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    first = source / "IMG_0001.jpg"
    second = source / "IMG_0002.jpg"
    sidecar = source / "IMG_0002.xmp"
    first.write_bytes(b"duplicate-bytes")
    second.write_bytes(b"duplicate-bytes")
    sidecar.write_bytes(b"xmp")

    scan_result = scan_exact_duplicates(DuplicateScanConfig(source_dirs=[source]))
    decisions = {build_exact_group_id(scan_result.exact_groups[0]): str(first)}
    bundle = build_duplicate_workflow_bundle(scan_result.exact_groups, decisions, "delete")
    execution_result = run_duplicate_execution_preview(bundle.execution_preview, apply=True)

    exit_code = determine_duplicate_cli_exit_code(
        scan_result,
        execution_result,
        apply_requested=True,
    )

    assert exit_code == 3


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
    assert payload["execution_status"] == "preview_only"
    assert payload["recommended_exit_code"] == 0
    assert payload["execution_run"]["processed_rows"] == 1
    assert payload["execution_run"]["entries"][0]["outcome"] == "preview-trash"
