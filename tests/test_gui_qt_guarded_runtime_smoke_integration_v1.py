from __future__ import annotations

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_guarded_runtime_smoke_integration_builds_real_shell_route_without_qt() -> None:
    model = build_gui_shell_model(active_page_id="dashboard")

    bundle = build_guarded_qt_runtime_smoke_integration(model)

    assert bundle["kind"] == "guarded_qt_runtime_smoke_integration"
    assert bundle["page_id"] == "runtime-smoke"
    assert bundle["page_model"]["kind"] == "qt_runtime_smoke_page_model"
    assert bundle["page_handoff"]["ready_for_shell_registration"] is True
    assert bundle["shell_bundle"]["ready_for_shell"] is True
    assert bundle["wiring_bundle"]["ready_for_guarded_shell_wiring"] is True
    assert bundle["summary"]["ready_for_shell_route"] is True
    assert bundle["summary"]["opens_window"] is False
    assert bundle["summary"]["executes_commands"] is False


def test_guarded_runtime_smoke_integration_stays_manual_for_result_acceptance() -> None:
    model = build_gui_shell_model(active_page_id="people-review", language="de")

    bundle = build_guarded_qt_runtime_smoke_integration(model)

    assert bundle["language"] == "de"
    assert bundle["manual_readiness"]["ready_to_start_manual_smoke"] is True
    assert bundle["manual_readiness"]["accepted_after_results"] is False
    assert bundle["result_bundle"]["summary"]["accepted"] is False
    assert bundle["capabilities"]["requires_pyside6"] is False
