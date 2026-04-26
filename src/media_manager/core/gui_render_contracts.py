from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_component_registry import build_component_registry, validate_widget_types
from .gui_dashboard_renderer import build_dashboard_render_spec
from .gui_people_review_renderer import build_people_review_render_spec
from .gui_table_renderer import build_table_render_spec
from .gui_visual_tokens import build_visual_tokens
from .gui_widget_specs import build_text_spec, build_widget_spec, summarize_widget_tree

RENDER_CONTRACT_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_page_render_contract(
    page_model: Mapping[str, Any],
    *,
    theme_payload: Mapping[str, Any] | None = None,
    density: str | None = None,
    target: str = "qt",
) -> dict[str, object]:
    kind = str(page_model.get("kind") or "")
    if kind == "dashboard_page":
        render_spec = build_dashboard_render_spec(page_model)
    elif kind == "people_review_page":
        render_spec = build_people_review_render_spec(page_model)
    elif kind in {"table_page", "profiles_page"}:
        render_spec = build_table_render_spec(page_model, table_id=str(page_model.get("page_id") or "table"))
    else:
        root = build_widget_spec(
            str(page_model.get("page_id") or "page"),
            "section",
            title=str(page_model.get("title") or "Page"),
            children=[build_text_spec("empty", str(page_model.get("empty_state") or page_model.get("description") or ""))],
        )
        render_spec = {
            "schema_version": RENDER_CONTRACT_SCHEMA_VERSION,
            "kind": "generic_render_spec",
            "page_id": page_model.get("page_id"),
            "root": root,
            "summary": summarize_widget_tree(root),
        }

    registry = build_component_registry()
    root_widget = _mapping(render_spec.get("root"))
    validation = validate_widget_types(registry, root_widget)
    return {
        "schema_version": RENDER_CONTRACT_SCHEMA_VERSION,
        "kind": "page_render_contract",
        "target": str(target or "qt"),
        "page_id": page_model.get("page_id"),
        "page_kind": kind,
        "tokens": build_visual_tokens(theme_payload=theme_payload, density=density or str(page_model.get("density") or "comfortable")),
        "component_registry": registry,
        "render_spec": render_spec,
        "validation": validation,
        "ready_to_render": bool(validation.get("valid")),
    }


def summarize_render_contract(contract: Mapping[str, Any]) -> dict[str, object]:
    validation = _mapping(contract.get("validation"))
    render_spec = _mapping(contract.get("render_spec"))
    summary = _mapping(render_spec.get("summary"))
    return {
        "schema_version": RENDER_CONTRACT_SCHEMA_VERSION,
        "page_id": contract.get("page_id"),
        "target": contract.get("target"),
        "ready_to_render": contract.get("ready_to_render"),
        "widget_count": summary.get("widget_count", 0),
        "missing_widget_types": validation.get("missing_widget_types", []),
    }


__all__ = ["RENDER_CONTRACT_SCHEMA_VERSION", "build_page_render_contract", "summarize_render_contract"]
