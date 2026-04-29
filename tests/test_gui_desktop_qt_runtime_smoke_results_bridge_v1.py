from __future__ import annotations

import sys

from media_manager.core.gui_shell_model import build_gui_shell_model
from media_manager.gui_desktop_qt import (
    attach_guarded_qt_runtime_smoke_to_shell_model,
    build_guarded_qt_runtime_smoke_plan,
    guarded_qt_runtime_smoke_plan_to_pretty_json,
)


def _passing_results() -> list[dict[str, object]]:
    return [
        {"check_id": "launch-window", "passed": True},
        {"check_id": "navigation-visible", "passed": True},
        {"check_id": "no-auto-execution", "passed": True},
        {"check_id": "local-only", "passed": True},
    ]


def test_desktop_guarded_plan_accepts_injected_manual_results() -> None:
    plan = build_guarded_qt_runtime_smoke_plan(
        build_gui_shell_model(active_page_id="dashboard"),
        results=_passing_results(),
        reviewer="manual-operator",
    )

    assert plan["smoke_report"]["reviewer"] == "manual-operator"
    assert plan["smoke_report"]["summary"]["evidence_complete"] is True
    assert plan["result_bundle"]["summary"]["accepted"] is True
    assert plan["manual_readiness"]["accepted_after_results"] is True
    assert plan["summary"]["accepted_after_results"] is True


def test_desktop_guarded_plan_json_accepts_injected_manual_results() -> None:
    text = guarded_qt_runtime_smoke_plan_to_pretty_json(
        build_gui_shell_model(active_page_id="dashboard"),
        results=_passing_results(),
    )

    assert '"accepted_after_results": true' in text
    assert '"opens_window": false' in text


def test_attached_shell_model_can_carry_manual_results_without_qt() -> None:
    sys.modules.pop("PySide6", None)

    shell = attach_guarded_qt_runtime_smoke_to_shell_model(
        build_gui_shell_model(active_page_id="dashboard"),
        activate=True,
        results=_passing_results(),
    )

    assert shell["active_page_id"] == "runtime-smoke"
    assert shell["page"]["presenter"]["metrics"]["evidence_complete"] is True
    assert shell["runtime_smoke"]["summary"]["accepted_after_results"] is True
    assert "PySide6" not in sys.modules
