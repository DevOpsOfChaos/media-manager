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


def test_all_result_bundle_parts_remain_headless_local_and_non_executing() -> None:
    bundle = build_qt_runtime_smoke_desktop_result_bundle(passing_results())
    cards = build_qt_runtime_smoke_desktop_result_cards(bundle)
    parts = [
        bundle,
        bundle["validation"],
        bundle["audit"],
        bundle["decision"],
        bundle["report"],
        bundle["export"],
        bundle["snapshot"],
        cards,
    ]

    for part in parts:
        assert part["capabilities"]["requires_pyside6"] is False
        assert part["capabilities"]["opens_window"] is False
        assert part["capabilities"]["executes_commands"] is False
        assert part["capabilities"]["local_only"] is True
