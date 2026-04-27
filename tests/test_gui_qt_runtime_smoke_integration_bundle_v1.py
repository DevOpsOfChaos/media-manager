from __future__ import annotations


def sample_adapter_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_adapter_bundle",
        "ready_for_qt_runtime": ready,
        "summary": {"problem_count": problems, "local_only": True, "ready_for_qt_runtime": ready},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }


def sample_page_handoff(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_page_handoff",
        "ready_for_shell_registration": ready,
        "summary": {"problem_count": problems, "local_only": True, "ready_for_shell_registration": ready},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }


def sample_shell_bundle(*, ready: bool = True, problems: int = 0) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_shell_bundle",
        "ready_for_shell": ready,
        "summary": {"problem_count": problems, "local_only": True, "ready_for_shell": ready},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

from media_manager.core.gui_qt_runtime_smoke_integration_bundle import build_qt_runtime_smoke_integration_bundle


def test_integration_bundle_marks_clean_chain_ready_for_guarded_shell_wiring() -> None:
    bundle = build_qt_runtime_smoke_integration_bundle(
        adapter_bundle=sample_adapter_bundle(),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )

    assert bundle["kind"] == "qt_runtime_smoke_integration_bundle"
    assert bundle["ready_for_guarded_shell_wiring"] is True
    assert bundle["summary"]["problem_count"] == 0
    assert bundle["summary"]["risk_level"] == "low"
    assert bundle["summary"]["opens_window"] is False
    assert bundle["summary"]["executes_commands"] is False


def test_integration_bundle_blocks_when_shell_bundle_has_problem() -> None:
    bundle = build_qt_runtime_smoke_integration_bundle(
        adapter_bundle=sample_adapter_bundle(),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(ready=False, problems=1),
    )

    assert bundle["ready_for_guarded_shell_wiring"] is False
    assert bundle["summary"]["problem_count"] > 0
    assert bundle["gate"]["ready"] is False
