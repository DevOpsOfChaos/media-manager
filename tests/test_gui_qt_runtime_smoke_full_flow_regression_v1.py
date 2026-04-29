from __future__ import annotations

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_full_flow_connects_adapter_page_shell_wiring_and_desktop_start() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model(active_page_id="dashboard"))

    assert bundle["adapter_bundle"]["ready_for_qt_runtime"] is True
    assert bundle["page_handoff"]["ready_for_shell_registration"] is True
    assert bundle["integration_bundle"]["ready_for_guarded_shell_wiring"] is True
    assert bundle["wiring_bundle"]["ready_for_guarded_shell_wiring"] is True
    assert bundle["rehearsal_bundle"]["ready_for_manual_desktop_smoke"] is True
    assert bundle["start_bundle"]["ready_for_manual_desktop_start"] is True


def test_full_flow_keeps_acceptance_blocked_until_manual_results_exist() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model(active_page_id="dashboard"))

    assert bundle["result_bundle"]["summary"]["result_count"] == 0
    assert bundle["acceptance_bundle"]["accepted"] is False
    assert bundle["summary"]["ready_to_start_manual_smoke"] is True
