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

from media_manager.core.gui_qt_runtime_smoke_integration_matrix import build_qt_runtime_smoke_integration_matrix


def test_integration_matrix_summarizes_ready_layers() -> None:
    matrix = build_qt_runtime_smoke_integration_matrix(
        adapter_bundle=sample_adapter_bundle(),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )

    assert matrix["summary"]["row_count"] == 3
    assert matrix["summary"]["ready_count"] == 3
    assert matrix["summary"]["all_ready"] is True
    assert matrix["summary"]["opens_window_count"] == 0
    assert matrix["summary"]["executes_commands_count"] == 0
    assert matrix["summary"]["all_local_only"] is True


def test_integration_matrix_tracks_blocked_layer() -> None:
    matrix = build_qt_runtime_smoke_integration_matrix(
        adapter_bundle=sample_adapter_bundle(ready=False, problems=1),
        page_handoff=sample_page_handoff(),
        shell_bundle=sample_shell_bundle(),
    )

    assert matrix["summary"]["all_ready"] is False
    assert matrix["summary"]["problem_count_total"] == 1
