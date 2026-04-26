from __future__ import annotations

from collections.abc import Mapping

THEME_SCHEMA_VERSION = "1.0"
DEFAULT_THEME = "modern-dark"
SUPPORTED_THEMES = ("modern-dark", "modern-light", "system")

_THEME_TOKENS: dict[str, dict[str, str]] = {
    "modern-dark": {
        "background": "#0f172a",
        "surface": "#111827",
        "surface_alt": "#1f2937",
        "text": "#f8fafc",
        "muted_text": "#94a3b8",
        "accent": "#38bdf8",
        "accent_strong": "#0ea5e9",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "border": "#334155",
    },
    "modern-light": {
        "background": "#f8fafc",
        "surface": "#ffffff",
        "surface_alt": "#eef2ff",
        "text": "#0f172a",
        "muted_text": "#475569",
        "accent": "#0284c7",
        "accent_strong": "#0369a1",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "border": "#cbd5e1",
    },
}


def normalize_theme(theme: str | None) -> str:
    value = str(theme or DEFAULT_THEME).strip().lower().replace("_", "-")
    if value in SUPPORTED_THEMES:
        return value
    return DEFAULT_THEME


def resolve_theme_tokens(theme: str | None = None) -> dict[str, str]:
    normalized = normalize_theme(theme)
    if normalized == "system":
        normalized = DEFAULT_THEME
    return dict(_THEME_TOKENS[normalized])


def build_theme_payload(theme: str | None = None) -> dict[str, object]:
    normalized = normalize_theme(theme)
    return {
        "schema_version": THEME_SCHEMA_VERSION,
        "theme": normalized,
        "resolved_theme": DEFAULT_THEME if normalized == "system" else normalized,
        "supported_themes": list(SUPPORTED_THEMES),
        "tokens": resolve_theme_tokens(normalized),
    }


def build_qt_stylesheet(theme: str | None = None) -> str:
    token = resolve_theme_tokens(theme)
    return f"""
QMainWindow, QWidget {{
    background-color: {token['background']};
    color: {token['text']};
    font-family: Segoe UI, Inter, Arial, sans-serif;
    font-size: 10.5pt;
}}
QFrame#Sidebar {{
    background-color: {token['surface']};
    border-right: 1px solid {token['border']};
}}
QLabel#AppTitle {{
    font-size: 20pt;
    font-weight: 700;
    color: {token['text']};
}}
QLabel#PageTitle {{
    font-size: 22pt;
    font-weight: 700;
    color: {token['text']};
}}
QLabel#Muted {{
    color: {token['muted_text']};
}}
QPushButton {{
    border: 1px solid {token['border']};
    border-radius: 12px;
    padding: 10px 14px;
    background-color: {token['surface_alt']};
    color: {token['text']};
}}
QPushButton:hover {{
    border-color: {token['accent']};
}}
QPushButton:checked {{
    background-color: {token['accent_strong']};
    border-color: {token['accent']};
    color: #ffffff;
}}
QFrame#Card {{
    background-color: {token['surface']};
    border: 1px solid {token['border']};
    border-radius: 18px;
}}
QStatusBar {{
    background-color: {token['surface']};
    color: {token['muted_text']};
}}
QScrollArea {{
    border: none;
}}
""".strip()


def merge_theme_into_model(model: Mapping[str, object], *, theme: str | None = None) -> dict[str, object]:
    return {**dict(model), "theme": build_theme_payload(theme)}


__all__ = [
    "DEFAULT_THEME",
    "SUPPORTED_THEMES",
    "THEME_SCHEMA_VERSION",
    "build_qt_stylesheet",
    "build_theme_payload",
    "merge_theme_into_model",
    "normalize_theme",
    "resolve_theme_tokens",
]
