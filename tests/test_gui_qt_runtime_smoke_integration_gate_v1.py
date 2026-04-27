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

from media_manager.core.gui_qt_runtime_smoke_integration_gate import evaluate_qt_runtime_smoke_integration_gate
from media_manager.core.gui_qt_runtime_smoke_integration_matrix import build_qt_runtime_smoke_integration_matrix


def test_integration_gate_allows_clean_matrix() -> None:
    matrix = build_qt_runtime_smoke_integration_matrix(
        adapter_bundle=sample_adapter_bundle(),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )
    gate = evaluate_qt_runtime_smoke_integration_gate(matrix)

    assert gate["ready"] is True
    assert gate["decision"] == "ready_for_guarded_shell_integration"
    assert gate["problem_count"] == 0


def test_integration_gate_blocks_problem_matrix() -> None:
    matrix = build_qt_runtime_smoke_integration_matrix(
        adapter_bundle=sample_adapter_bundle(ready=False, problems=1),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )
    gate = evaluate_qt_runtime_smoke_integration_gate(matrix)

    assert gate["ready"] is False
    codes = {problem["code"] for problem in gate["problems"]}
    assert "not_all_layers_ready" in codes
    assert "integration_layers_have_problems" in codes
