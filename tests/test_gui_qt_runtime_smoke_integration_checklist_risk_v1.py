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

from media_manager.core.gui_qt_runtime_smoke_integration_checklist import build_qt_runtime_smoke_integration_checklist
from media_manager.core.gui_qt_runtime_smoke_integration_gate import evaluate_qt_runtime_smoke_integration_gate
from media_manager.core.gui_qt_runtime_smoke_integration_matrix import build_qt_runtime_smoke_integration_matrix
from media_manager.core.gui_qt_runtime_smoke_integration_risk import build_qt_runtime_smoke_integration_risk


def test_checklist_and_risk_are_low_for_ready_gate() -> None:
    matrix = build_qt_runtime_smoke_integration_matrix(
        adapter_bundle=sample_adapter_bundle(),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )
    gate = evaluate_qt_runtime_smoke_integration_gate(matrix)
    checklist = build_qt_runtime_smoke_integration_checklist(gate)
    risk = build_qt_runtime_smoke_integration_risk(gate, checklist)

    assert checklist["summary"]["failed_required_count"] == 0
    assert checklist["summary"]["ready"] is True
    assert risk["level"] == "low"
    assert risk["allows_next_shell_wiring"] is True


def test_checklist_and_risk_block_problem_gate() -> None:
    matrix = build_qt_runtime_smoke_integration_matrix(
        adapter_bundle=sample_adapter_bundle(ready=False, problems=2),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )
    gate = evaluate_qt_runtime_smoke_integration_gate(matrix)
    checklist = build_qt_runtime_smoke_integration_checklist(gate)
    risk = build_qt_runtime_smoke_integration_risk(gate, checklist)

    assert checklist["summary"]["failed_required_count"] > 0
    assert risk["level"] in {"medium", "high"}
    assert risk["allows_next_shell_wiring"] is False
