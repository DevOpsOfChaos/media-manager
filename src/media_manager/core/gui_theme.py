from __future__ import annotations

from typing import Any

THEME_SCHEMA_VERSION = "1.1"
DEFAULT_THEME = "modern-dark"
SUPPORTED_THEMES = ("modern-dark", "modern-light", "system")

_PALETTES = {
    "modern-dark": {
        "background": "#0f172a",
        "surface": "#111827",
        "surface_alt": "#1f2937",
        "text": "#e5e7eb",
        "muted": "#94a3b8",
        "accent": "#60a5fa",
        "accent_text": "#0f172a",
        "border": "#334155",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#fb7185",
    },
    "modern-light": {
        "background": "#f8fafc",
        "surface": "#ffffff",
        "surface_alt": "#e2e8f0",
        "text": "#0f172a",
        "muted": "#475569",
        "accent": "#2563eb",
        "accent_text": "#ffffff",
        "border": "#cbd5e1",
        "success": "#059669",
        "warning": "#d97706",
        "danger": "#e11d48",
    },
}


def normalize_theme(theme: str | None) -> str:
    value = str(theme or DEFAULT_THEME).strip().lower().replace("_", "-")
    if value == "dark":
        return "modern-dark"
    if value == "light":
        return "modern-light"
    if value not in SUPPORTED_THEMES:
        return DEFAULT_THEME
    return value


def palette_for_theme(theme: str | None) -> dict[str, str]:
    normalized = normalize_theme(theme)
    if normalized == "system":
        normalized = DEFAULT_THEME
    return dict(_PALETTES[normalized])


def build_theme_payload(theme: str | None = None) -> dict[str, Any]:
    normalized = normalize_theme(theme)
    palette = palette_for_theme(normalized)
    tokens = dict(palette)
    return {
        "schema_version": THEME_SCHEMA_VERSION,
        "theme": normalized,
        # ``palette`` is the newer explicit name used by the Qt shell.
        "palette": palette,
        # ``tokens`` is kept as a compatibility alias for earlier GUI model tests
        # and callers that read theme colors generically.
        "tokens": tokens,
        "radius": {"sm": 8, "md": 14, "lg": 20, "xl": 28},
        "spacing": {"xs": 6, "sm": 10, "md": 16, "lg": 24, "xl": 32},
        "typography": {"font_family": "Segoe UI", "title_size": 28, "body_size": 14, "caption_size": 12},
    }


def build_qt_stylesheet(theme: str | None = None) -> str:
    palette = palette_for_theme(theme)
    return f"""
QWidget {{
    background: {palette['background']};
    color: {palette['text']};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 14px;
}}
QMainWindow, QScrollArea {{
    background: {palette['background']};
    border: none;
}}
QFrame#Sidebar {{
    background: {palette['surface']};
    border-right: 1px solid {palette['border']};
}}
QFrame#Card, QFrame#Section {{
    background: {palette['surface']};
    border: 1px solid {palette['border']};
    border-radius: 18px;
}}
QLabel#AppTitle {{
    font-size: 24px;
    font-weight: 700;
    color: {palette['text']};
}}
QLabel#PageTitle {{
    font-size: 30px;
    font-weight: 800;
    color: {palette['text']};
}}
QLabel#SectionTitle {{
    font-size: 20px;
    font-weight: 700;
    color: {palette['text']};
}}
QLabel#CardTitle {{
    font-size: 17px;
    font-weight: 700;
    color: {palette['text']};
}}
QLabel#Muted {{
    color: {palette['muted']};
}}
QLabel#MetricText {{
    color: {palette['text']};
    font-weight: 600;
}}
QPushButton {{
    background: {palette['surface_alt']};
    color: {palette['text']};
    border: 1px solid {palette['border']};
    border-radius: 12px;
    padding: 10px 12px;
    text-align: left;
}}
QPushButton:hover {{
    border-color: {palette['accent']};
}}
QPushButton:checked {{
    background: {palette['accent']};
    color: {palette['accent_text']};
    border-color: {palette['accent']};
    font-weight: 700;
}}
QPushButton[groupButton="true"] {{
    min-height: 56px;
}}
QTableWidget {{
    background: {palette['surface']};
    alternate-background-color: {palette['surface_alt']};
    gridline-color: {palette['border']};
    border: 1px solid {palette['border']};
    border-radius: 14px;
}}
QHeaderView::section {{
    background: {palette['surface_alt']};
    color: {palette['text']};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {palette['border']};
    font-weight: 700;
}}
QStatusBar {{
    background: {palette['surface']};
    color: {palette['muted']};
    border-top: 1px solid {palette['border']};
}}
"""


__all__ = [
    "DEFAULT_THEME",
    "SUPPORTED_THEMES",
    "THEME_SCHEMA_VERSION",
    "build_qt_stylesheet",
    "build_theme_payload",
    "normalize_theme",
    "palette_for_theme",
]
