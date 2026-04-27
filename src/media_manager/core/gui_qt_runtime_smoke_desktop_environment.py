from __future__ import annotations

QT_RUNTIME_SMOKE_DESKTOP_ENVIRONMENT_SCHEMA_VERSION = "1.0"

def build_qt_runtime_smoke_desktop_environment(*, platform: str = "Windows", python_executable: str = "python", gui_extra_installed: bool | None = None) -> dict[str, object]:
    extra_known = gui_extra_installed is not None
    failed_required = 0 if python_executable else 1
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_ENVIRONMENT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_environment",
        "platform": platform,
        "python_executable": python_executable,
        "gui_extra_installed": gui_extra_installed,
        "gui_extra_known": extra_known,
        "install_hint": 'python -m pip install -e ".[gui]"',
        "checks": [
            {"id": "python-available", "passed": bool(python_executable), "required": True},
            {"id": "windows-primary", "passed": platform.lower().startswith("win"), "required": False},
            {"id": "gui-extra-known", "passed": extra_known, "required": False},
        ],
        "summary": {"check_count": 3, "failed_required_count": failed_required, "gui_extra_known": extra_known, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_ENVIRONMENT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_environment"]
