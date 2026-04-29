from __future__ import annotations

import sys

from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import (
    attach_guarded_qt_runtime_smoke_to_shell_model,
    build_guarded_qt_runtime_smoke_plan,
)


def test_guarded_runtime_smoke_page_status_matches_manual_readiness_summary() -> None:
    shell = build_gui_shell_model(active_page_id="runtime-smoke")

    plan = build_guarded_qt_runtime_smoke_plan(shell)
    page = plan["page_model"]
    presenter = page["presenter"]
    metrics = presenter["metrics"]

    assert plan["summary"]["ready_for_shell_route"] is True
    assert plan["summary"]["ready_to_start_manual_smoke"] is True
    assert plan["summary"]["problem_count"] == 0
    assert presenter["status"] == "ready"
    assert presenter["severity"] == "success"
    assert metrics["ready_for_runtime_review"] is True
    assert metrics["ready_to_start_manual_smoke"] is True
    assert metrics["evidence_complete"] is False
    assert page["summary"]["ready_to_start_manual_smoke"] is True
    assert "Fix failing runtime smoke checks" not in str(presenter["recommended_next_step"])


def test_attached_runtime_smoke_shell_model_uses_ready_page_model() -> None:
    shell = build_gui_shell_model(active_page_id="dashboard")

    attached = attach_guarded_qt_runtime_smoke_to_shell_model(shell, activate=True)
    page = attached["page"]
    runtime_smoke = attached["runtime_smoke"]

    assert attached["active_page_id"] == "runtime-smoke"
    assert page["kind"] == "qt_runtime_smoke_page_model"
    assert page["presenter"]["status"] == "ready"
    assert page["summary"]["ready_to_start_manual_smoke"] is True
    assert runtime_smoke["summary"]["ready_to_start_manual_smoke"] is True
    assert attached["status_bar"]["text"]


def test_guarded_runtime_smoke_plan_still_does_not_import_pyside6() -> None:
    sys.modules.pop("PySide6", None)
    shell = build_gui_shell_model(active_page_id="runtime-smoke")

    plan = build_guarded_qt_runtime_smoke_plan(shell)

    assert "PySide6" not in sys.modules
    assert plan["capabilities"]["requires_pyside6"] is False
    assert plan["capabilities"]["opens_window"] is False
    assert plan["capabilities"]["executes_commands"] is False
