from __future__ import annotations


def passing_results() -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_result_collector",
        "results": [
            {"check_id": "read-command", "label": "Read command", "required": True, "passed": True},
            {"check_id": "confirm-local-only", "label": "Confirm local-only", "required": True, "passed": True},
            {"check_id": "confirm-window-title", "label": "Confirm window title", "required": True, "passed": True, "evidence_path": "local/screens/window.png"},
            {"check_id": "confirm-active-page", "label": "Confirm active page", "required": True, "passed": True},
            {"check_id": "confirm-no-auto-apply", "label": "Confirm no auto apply", "required": True, "passed": True},
        ],
    }


def failing_results() -> dict[str, object]:
    payload = passing_results()
    payload["results"][4]["passed"] = False
    payload["results"][4]["note"] = "Apply button started unexpectedly"
    return payload


def missing_results() -> dict[str, object]:
    payload = passing_results()
    payload["results"][2]["passed"] = None
    return payload

from media_manager.core.gui_qt_runtime_smoke_desktop_result_bundle import build_qt_runtime_smoke_desktop_result_bundle
from media_manager.core.gui_qt_runtime_smoke_desktop_result_export import build_qt_runtime_smoke_desktop_result_export
from media_manager.core.gui_qt_runtime_smoke_desktop_result_history import build_qt_runtime_smoke_desktop_result_history, build_qt_runtime_smoke_desktop_result_history_entry
from media_manager.core.gui_qt_runtime_smoke_desktop_result_snapshot import build_qt_runtime_smoke_desktop_result_snapshot


def test_result_export_redacts_evidence_paths() -> None:
    bundle = build_qt_runtime_smoke_desktop_result_bundle(passing_results())
    export = build_qt_runtime_smoke_desktop_result_export(bundle["report"])

    assert export["privacy"]["metadata_only"] is True
    assert export["privacy"]["evidence_paths_redacted"] is True
    assert "evidence_path" not in export["results"][2]
    assert export["results"][2]["has_evidence_path"] is True


def test_result_history_and_snapshot_are_stable() -> None:
    bundle = build_qt_runtime_smoke_desktop_result_bundle(passing_results())
    entry = build_qt_runtime_smoke_desktop_result_history_entry(bundle["report"], recorded_at_utc="2026-04-27T20:00:00Z")
    history = build_qt_runtime_smoke_desktop_result_history([entry])
    snapshot_a = build_qt_runtime_smoke_desktop_result_snapshot(bundle["report"])
    snapshot_b = build_qt_runtime_smoke_desktop_result_snapshot(bundle["report"])

    assert history["summary"]["entry_count"] == 1
    assert history["summary"]["accepted_count"] == 1
    assert snapshot_a["payload_hash"] == snapshot_b["payload_hash"]
    assert len(snapshot_a["payload_hash"]) == 64
