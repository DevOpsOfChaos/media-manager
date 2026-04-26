from __future__ import annotations

from collections.abc import Mapping

THEME_SCHEMA_VERSION = "1.1"
DEFAULT_THEME = "modern-dark"
SUPPORTED_THEMES = ("modern-dark", "modern-light", "system")

_THEME_TOKENS: dict[str, dict[str, str]] = {
    "modern-dark": {
        "background": "#0b1020",
        "background_soft": "#10172a",
        "surface": "#111827",
        "surface_alt": "#1f2937",
        "surface_elevated": "#172033",
        "text": "#f8fafc",
        "muted_text": "#94a3b8",
        "accent": "#38bdf8",
        "accent_strong": "#0ea5e9",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "border": "#334155",
        "shadow": "rgba(0,0,0,0.35)",
    },
    "modern-light": {
        "background": "#f8fafc",
        "background_soft": "#eef2ff",
        "surface": "#ffffff",
        "surface_alt": "#eef2ff",
        "surface_elevated": "#ffffff",
        "text": "#0f172a",
        "muted_text": "#475569",
        "accent": "#0284c7",
        "accent_strong": "#0369a1",
        "success": "#16a34a",
        "warning": "#d97706",
        "danger": "#dc2626",
        "border": "#cbd5e1",
        "shadow": "rgba(15,23,42,0.12)",
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
        "typography": {
            "font_family": "Segoe UI, Inter, Arial, sans-serif",
            "base_size": 11,
            "title_size": 24,
            "hero_size": 30,
        },
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
QFrame#TopBar {{
    background-color: {token['background_soft']};
    border-bottom: 1px solid {token['border']};
}}
QLabel#AppTitle {{
    font-size: 20pt;
    font-weight: 800;
    color: {token['text']};
}}
QLabel#PageTitle {{
    font-size: 24pt;
    font-weight: 800;
    color: {token['text']};
}}
QLabel#HeroTitle {{
    font-size: 30pt;
    font-weight: 800;
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
QPushButton:checked, QPushButton#PrimaryButton {{
    background-color: {token['accent_strong']};
    border-color: {token['accent']};
    color: #ffffff;
}}
QLineEdit {{
    border: 1px solid {token['border']};
    border-radius: 12px;
    padding: 10px 12px;
    background-color: {token['surface']};
    color: {token['text']};
}}
QFrame#Card, QFrame#HeroCard {{
    background-color: {token['surface_elevated']};
    border: 1px solid {token['border']};
    border-radius: 18px;
}}
QFrame#HeroCard {{
    background-color: {token['background_soft']};
}}
QTableWidget {{
    background-color: {token['surface']};
    alternate-background-color: {token['surface_alt']};
    border: 1px solid {token['border']};
    border-radius: 14px;
    gridline-color: {token['border']};
}}
QHeaderView::section {{
    background-color: {token['surface_alt']};
    color: {token['text']};
    padding: 8px;
    border: none;
}}
QStatusBar {{
    background-color: {token['surface']};
    color: {token['muted_text']};
}}
QScrollArea {{ border: none; }}
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
