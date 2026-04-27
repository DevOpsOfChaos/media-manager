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
from media_manager.core.gui_qt_runtime_smoke_desktop_result_cards import build_qt_runtime_smoke_desktop_result_cards
from media_manager.core.gui_qt_runtime_smoke_desktop_result_summary_text import summarize_qt_runtime_smoke_desktop_result_bundle


def test_result_bundle_cards_and_text_for_passing_results() -> None:
    bundle = build_qt_runtime_smoke_desktop_result_bundle(passing_results())
    cards = build_qt_runtime_smoke_desktop_result_cards(bundle)
    text = summarize_qt_runtime_smoke_desktop_result_bundle(bundle)

    assert bundle["accepted"] is True
    assert bundle["summary"]["decision"] == "accepted"
    assert cards["summary"]["card_count"] == 4
    assert "Accepted: True" in text
    assert bundle["capabilities"]["opens_window"] is False


def test_result_bundle_blocks_failing_results() -> None:
    bundle = build_qt_runtime_smoke_desktop_result_bundle(failing_results())

    assert bundle["accepted"] is False
    assert bundle["summary"]["failed_required_count"] == 1
    assert bundle["summary"]["problem_count"] > 0
