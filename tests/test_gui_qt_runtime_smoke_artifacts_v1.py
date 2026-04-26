from __future__ import annotations


def sample_smoke_report() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "kind": "qt_runtime_smoke_report",
        "active_page_id": "people-review",
        "reviewer": "Manuel",
        "handoff_ready": True,
        "launch_ready": True,
        "ready_for_release_gate": True,
        "session": {
            "kind": "qt_runtime_smoke_session",
            "active_page_id": "people-review",
            "complete": True,
            "summary": {
                "check_count": 4,
                "result_count": 4,
                "missing_required_count": 0,
                "failed_required_count": 0,
                "privacy_check_count": 2,
            },
            "missing_required_checks": [],
            "failed_required_checks": [],
            "results": [
                {
                    "kind": "qt_runtime_smoke_result",
                    "check_id": "launch-window",
                    "passed": True,
                    "required": True,
                    "category": "startup",
                    "note": "ok",
                    "evidence_path": "C:/Users/mries/Pictures/screenshot.png",
                },
                {
                    "kind": "qt_runtime_smoke_result",
                    "check_id": "local-only",
                    "passed": True,
                    "required": True,
                    "category": "privacy",
                    "note": "no upload",
                    "evidence_path": None,
                },
            ],
        },
        "audit": {
            "kind": "qt_runtime_smoke_audit",
            "valid": True,
            "problem_count": 0,
            "problems": [],
            "summary": {"privacy_check_count": 2, "passed_privacy_check_count": 2},
        },
        "summary": {
            "check_count": 4,
            "result_count": 4,
            "missing_required_count": 0,
            "failed_required_count": 0,
            "privacy_check_count": 2,
            "problem_count": 0,
            "ready_for_release_gate": True,
        },
    }

from media_manager.core.gui_qt_runtime_smoke_artifacts import (
    build_qt_runtime_smoke_artifact_manifest,
    build_qt_runtime_smoke_artifact_record,
)
from media_manager.core.gui_qt_runtime_smoke_export import build_qt_runtime_smoke_export_bundle


def test_smoke_artifact_record_hashes_metadata_payload() -> None:
    payload = build_qt_runtime_smoke_export_bundle(sample_smoke_report())
    record = build_qt_runtime_smoke_artifact_record("smoke-export", path="out/smoke-export.json", payload=payload)

    assert record["artifact_id"] == "smoke-export"
    assert record["filename"] == "smoke-export.json"
    assert len(record["payload_hash"]) == 64
    assert record["metadata_only"] is True
    assert record["contains_sensitive_media"] is False


def test_smoke_artifact_manifest_is_local_metadata_only() -> None:
    report = sample_smoke_report()
    export = build_qt_runtime_smoke_export_bundle(report)
    manifest = build_qt_runtime_smoke_artifact_manifest(
        {"smoke-report": report, "smoke-export": export},
        root_dir="runtime-smoke",
    )

    assert manifest["summary"]["artifact_count"] == 2
    assert manifest["summary"]["metadata_only_count"] == 2
    assert manifest["summary"]["sensitive_media_count"] == 0
    assert manifest["summary"]["all_local_only"] is True
