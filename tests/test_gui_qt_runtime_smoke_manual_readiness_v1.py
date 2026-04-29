from __future__ import annotations

from media_manager.core.gui_qt_guarded_runtime_smoke_integration import build_guarded_qt_runtime_smoke_integration
from media_manager.core.gui_qt_runtime_smoke_manual_readiness import summarize_qt_runtime_smoke_manual_readiness
from media_manager.core.gui_shell_model import build_gui_shell_model


def test_manual_readiness_is_start_ready_but_not_result_accepted_without_results() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())
    readiness = bundle["manual_readiness"]

    assert readiness["ready_to_start_manual_smoke"] is True
    assert readiness["accepted_after_results"] is False
    assert readiness["summary"]["opens_window"] is False
    assert readiness["summary"]["executes_commands"] is False
    assert "Ready to start manual smoke: True" in summarize_qt_runtime_smoke_manual_readiness(readiness)


def test_desktop_launch_dry_run_never_executes_or_opens_window() -> None:
    bundle = build_guarded_qt_runtime_smoke_integration(build_gui_shell_model())
    dry_run = bundle["dry_run"]

    assert dry_run["ready"] is True
    assert dry_run["execution_policy"]["mode"] == "dry_run_only"
    assert dry_run["execution_policy"]["opens_window"] is False
    assert dry_run["execution_policy"]["executes_commands"] is False
