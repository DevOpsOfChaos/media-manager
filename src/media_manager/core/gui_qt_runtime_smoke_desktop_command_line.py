from __future__ import annotations

QT_RUNTIME_SMOKE_DESKTOP_COMMAND_LINE_SCHEMA_VERSION = "1.0"

def build_qt_runtime_smoke_desktop_command_line(*, language: str = "de", theme: str = "modern-dark", active_page: str = "runtime-smoke", entry_point: str = "media-manager-gui") -> dict[str, object]:
    lang = "de" if language == "de" else "en"
    argv = [entry_point, "--language", lang, "--theme", theme, "--active-page", active_page]
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_COMMAND_LINE_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_command_line",
        "entry_point": entry_point,
        "argv": argv,
        "display_command": " ".join(argv),
        "language": lang,
        "theme": theme,
        "active_page": active_page,
        "execution_policy": {"mode": "manual_only", "requires_confirmation": True, "executes_immediately": False, "opens_window": False},
        "summary": {"arg_count": len(argv), "manual_only": True, "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_COMMAND_LINE_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_command_line"]
