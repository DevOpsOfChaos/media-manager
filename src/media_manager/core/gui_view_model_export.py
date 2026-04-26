from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import json
from typing import Any

from .gui_render_contracts import build_page_render_contract, summarize_render_contract

VIEW_MODEL_EXPORT_SCHEMA_VERSION = "1.0"


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def build_view_model_export(
    *,
    page_model: Mapping[str, Any],
    out_dir: str | Path,
    theme_payload: Mapping[str, Any] | None = None,
    density: str | None = None,
) -> dict[str, object]:
    root = Path(out_dir)
    contract = build_page_render_contract(page_model, theme_payload=theme_payload, density=density)
    return {
        "schema_version": VIEW_MODEL_EXPORT_SCHEMA_VERSION,
        "kind": "gui_view_model_export",
        "out_dir": str(root),
        "page_id": page_model.get("page_id"),
        "files": {
            "page_model": "page_model.json",
            "render_contract": "render_contract.json",
            "render_summary": "render_summary.json",
        },
        "summary": summarize_render_contract(contract),
        "sensitive": bool(page_model.get("page_id") == "people-review"),
    }


def write_view_model_export(
    *,
    page_model: Mapping[str, Any],
    out_dir: str | Path,
    theme_payload: Mapping[str, Any] | None = None,
    density: str | None = None,
) -> dict[str, object]:
    root = Path(out_dir)
    manifest = build_view_model_export(page_model=page_model, out_dir=root, theme_payload=theme_payload, density=density)
    contract = build_page_render_contract(page_model, theme_payload=theme_payload, density=density)
    write_json(root / "page_model.json", page_model)
    write_json(root / "render_contract.json", contract)
    write_json(root / "render_summary.json", summarize_render_contract(contract))
    write_json(root / "manifest.json", manifest)
    return {
        **manifest,
        "written_files": [
            str(root / "page_model.json"),
            str(root / "render_contract.json"),
            str(root / "render_summary.json"),
            str(root / "manifest.json"),
        ],
    }


__all__ = ["VIEW_MODEL_EXPORT_SCHEMA_VERSION", "build_view_model_export", "write_json", "write_view_model_export"]
