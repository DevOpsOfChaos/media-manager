from __future__ import annotations

def sample_rehearsal_bundle(*, ready: bool = True) -> dict[str, object]:
    return {
        "kind": "qt_runtime_smoke_desktop_rehearsal_bundle",
        "ready_for_manual_desktop_smoke": ready,
        "ready": ready,
        "summary": {"ready": ready, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "executes_commands": False, "local_only": True},
    }

from media_manager.core.gui_qt_runtime_smoke_desktop_command_line import build_qt_runtime_smoke_desktop_command_line
from media_manager.core.gui_qt_runtime_smoke_desktop_environment import build_qt_runtime_smoke_desktop_environment
from media_manager.core.gui_qt_runtime_smoke_desktop_window_contract import build_qt_runtime_smoke_desktop_window_contract

def test_environment_command_and_window_contract_are_manual_only() -> None:
    env = build_qt_runtime_smoke_desktop_environment(platform="Windows")
    command = build_qt_runtime_smoke_desktop_command_line(language="de")
    window = build_qt_runtime_smoke_desktop_window_contract()
    assert env["summary"]["failed_required_count"] == 0
    assert command["language"] == "de"
    assert "--active-page" in command["argv"]
    assert command["execution_policy"]["executes_immediately"] is False
    assert window["runtime_policy"]["constructs_window_now"] is False
    assert window["summary"]["opens_window"] is False
