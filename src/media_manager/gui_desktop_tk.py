from __future__ import annotations

from collections.abc import Mapping
import json
from typing import Any


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _page_text(page: Mapping[str, Any]) -> str:
    lines = [str(page.get("title") or page.get("page_id") or "Page")]
    kind = page.get("kind")
    if kind:
        lines.append(f"Kind: {kind}")
    overview = page.get("overview")
    if isinstance(overview, Mapping):
        lines.append("")
        lines.append("Overview")
        for key, value in sorted(overview.items()):
            lines.append(f"  {key}: {value}")
    cards = _as_list(page.get("cards"))
    if cards:
        lines.append("")
        lines.append("Cards")
        for card in cards:
            if isinstance(card, Mapping):
                lines.append(f"  - {card.get('title')}: {card.get('metrics', {})}")
    rows = _as_list(page.get("rows"))
    if rows:
        lines.append("")
        lines.append("Rows")
        for row in rows[:25]:
            lines.append(f"  - {row}")
    groups = _as_list(page.get("groups"))
    if groups:
        lines.append("")
        lines.append("People groups")
        for group in groups[:25]:
            if isinstance(group, Mapping):
                lines.append(f"  - {group.get('display_label') or group.get('group_id')} | {group.get('status')} | faces={group.get('face_count')}")
    if page.get("empty_state"):
        lines.append("")
        lines.append(str(page["empty_state"]))
    return "\n".join(lines)


def run_tk_gui(shell_model: Mapping[str, Any]) -> int:
    """Run a small stdlib Tkinter shell. Imported lazily so tests stay headless."""
    import tkinter as tk
    from tkinter import ttk

    window_payload = _as_mapping(shell_model.get("window"))
    app = _as_mapping(shell_model.get("application"))
    root = tk.Tk()
    root.title(str(window_payload.get("title") or app.get("title") or "Media Manager"))
    width = int(window_payload.get("width") or 1180)
    height = int(window_payload.get("height") or 760)
    root.geometry(f"{width}x{height}")

    container = ttk.Frame(root, padding=12)
    container.pack(fill="both", expand=True)
    header = ttk.Label(container, text=str(app.get("title") or "Media Manager"), font=("Segoe UI", 16, "bold"))
    header.pack(anchor="w")

    body = ttk.Frame(container)
    body.pack(fill="both", expand=True, pady=(12, 8))

    nav = ttk.Frame(body, width=220)
    nav.pack(side="left", fill="y", padx=(0, 12))
    content = ttk.Frame(body)
    content.pack(side="left", fill="both", expand=True)

    text = tk.Text(content, wrap="word", height=28)
    text.pack(fill="both", expand=True)
    text.insert("1.0", _page_text(_as_mapping(shell_model.get("page"))))
    text.configure(state="disabled")

    for item in _as_list(shell_model.get("navigation")):
        if not isinstance(item, Mapping):
            continue
        label = str(item.get("label") or item.get("id"))
        marker = "● " if item.get("active") else "  "
        button = ttk.Button(nav, text=marker + label, state="normal" if item.get("enabled", True) else "disabled")
        button.pack(fill="x", pady=2)

    status = _as_mapping(shell_model.get("status_bar"))
    status_label = ttk.Label(container, text=str(status.get("text") or "Ready."), anchor="w")
    status_label.pack(fill="x")
    root.mainloop()
    return 0


def shell_model_to_pretty_json(shell_model: Mapping[str, Any]) -> str:
    return json.dumps(dict(shell_model), indent=2, ensure_ascii=False)


__all__ = ["run_tk_gui", "shell_model_to_pretty_json"]
