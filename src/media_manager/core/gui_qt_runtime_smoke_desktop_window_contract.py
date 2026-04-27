from __future__ import annotations

QT_RUNTIME_SMOKE_DESKTOP_WINDOW_CONTRACT_SCHEMA_VERSION = "1.0"

def build_qt_runtime_smoke_desktop_window_contract(*, title: str = "Media Manager", initial_page: str = "runtime-smoke", width: int = 1280, height: int = 820) -> dict[str, object]:
    return {
        "schema_version": QT_RUNTIME_SMOKE_DESKTOP_WINDOW_CONTRACT_SCHEMA_VERSION,
        "kind": "qt_runtime_smoke_desktop_window_contract",
        "title": title,
        "initial_page": initial_page,
        "size": {"width": int(width), "height": int(height)},
        "minimum_size": {"width": 1024, "height": 720},
        "privacy_banner": {"visible": initial_page == "runtime-smoke", "text": "Runtime Smoke is local-only and does not upload people data."},
        "runtime_policy": {"lazy_pyside_import": True, "constructs_window_now": False, "opens_window_now": False, "executes_commands_now": False},
        "summary": {"privacy_banner_visible": initial_page == "runtime-smoke", "opens_window": False, "executes_commands": False, "local_only": True},
        "capabilities": {"requires_pyside6": False, "opens_window": False, "headless_testable": True, "executes_commands": False, "local_only": True},
    }

__all__ = ["QT_RUNTIME_SMOKE_DESKTOP_WINDOW_CONTRACT_SCHEMA_VERSION", "build_qt_runtime_smoke_desktop_window_contract"]
