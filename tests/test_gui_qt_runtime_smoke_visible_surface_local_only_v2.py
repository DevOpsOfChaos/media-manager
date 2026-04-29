from __future__ import annotations

from media_manager.core.gui_qt_runtime_smoke_adapter_bundle import build_qt_runtime_smoke_adapter_bundle
from media_manager.core.gui_qt_runtime_smoke_visible_surface import build_qt_runtime_smoke_visible_surface


def test_visible_surface_summary_exposes_local_only_for_adapter_validation() -> None:
    page_model = {
        "kind": "qt_runtime_smoke_page_model",
        "page_id": "runtime-smoke",
        "title": "Runtime Smoke",
        "presenter": {"metrics": {"ready_for_runtime_review": False}, "status": "pending", "severity": "info"},
        "table": {"columns": [], "rows": [], "summary": {"row_count": 0}},
        "detail": {"privacy": {"local_only": True, "network_required": False}},
        "actions": [],
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

    surface = build_qt_runtime_smoke_visible_surface(page_model)
    adapter = build_qt_runtime_smoke_adapter_bundle(surface)

    assert surface["summary"]["local_only"] is True
    assert adapter["ready_for_qt_runtime"] is True
    assert adapter["summary"]["problem_count"] == 0
