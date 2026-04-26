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

from media_manager.core.gui_qt_runtime_smoke_export import build_qt_runtime_smoke_export_bundle


def test_smoke_export_is_metadata_only_and_redacts_evidence_paths() -> None:
    bundle = build_qt_runtime_smoke_export_bundle(sample_smoke_report())

    result = bundle["session"]["results"][0]

    assert bundle["privacy"]["metadata_only"] is True
    assert bundle["privacy"]["contains_face_crops"] is False
    assert bundle["privacy"]["contains_embeddings"] is False
    assert bundle["privacy"]["evidence_paths_redacted"] is True
    assert "evidence_path" not in result
    assert result["has_evidence_path"] is True


def test_smoke_export_can_omit_results() -> None:
    bundle = build_qt_runtime_smoke_export_bundle(sample_smoke_report(), include_results=False)

    assert "results" not in bundle["session"]
    assert bundle["summary"]["ready_for_release_gate"] is True
