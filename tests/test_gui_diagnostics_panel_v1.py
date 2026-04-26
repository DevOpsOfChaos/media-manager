from media_manager.core.gui_diagnostics_panel import build_diagnostic_item, build_diagnostics_panel


def test_diagnostics_panel_sorts_errors_first() -> None:
    payload = build_diagnostics_panel(
        backend_status={"available": False, "next_action": "install backend"},
        bundle_validation={"valid": False, "problem_count": 2},
        model_health={"valid": True, "summary": "ok"},
    )

    assert payload["item_count"] == 3
    assert payload["error_count"] == 1
    assert payload["items"][0]["status"] == "error"


def test_diagnostic_item_normalizes_bad_status() -> None:
    item = build_diagnostic_item("x", "X", status="weird")

    assert item["status"] == "unknown"
