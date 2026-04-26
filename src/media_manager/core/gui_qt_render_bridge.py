from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .gui_qt_render_tree_snapshot import build_render_tree_snapshot
from .gui_qt_render_tree_validator import validate_render_tree
from .gui_qt_shell_render_tree import build_shell_render_tree, summarize_shell_render_tree
from .gui_qt_visible_desktop_plan import build_qt_visible_desktop_plan, desktop_plan_is_ready
from .gui_render_contracts import build_page_render_contract, summarize_render_contract

QT_RENDER_BRIDGE_SCHEMA_VERSION = "1.0"


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def build_qt_render_bridge(shell_model: Mapping[str, Any]) -> dict[str, object]:
    """Bridge the existing GUI shell model to a renderable, headless Qt tree.

    This is intentionally still a planning contract: it imports no PySide6,
    opens no window, and marks all execution as deferred. The real Qt desktop
    can consume the resulting tree in a later integration step.
    """

    desktop_plan = build_qt_visible_desktop_plan(shell_model)
    shell_tree = build_shell_render_tree(desktop_plan)
    root = _mapping(shell_tree.get("root"))
    validation = validate_render_tree(root)
    snapshot = build_render_tree_snapshot(root)
    page_model = _mapping(shell_model.get("page"))
    render_contract = build_page_render_contract(
        page_model,
        theme_payload=_mapping(shell_model.get("theme")),
        density=str(_mapping(shell_model.get("layout")).get("density") or "comfortable"),
        target="qt",
    )
    contract_summary = summarize_render_contract(render_contract)
    shell_summary = summarize_shell_render_tree(shell_tree)
    ready = bool(validation.get("valid")) and bool(desktop_plan_is_ready(desktop_plan)) and bool(render_contract.get("ready_to_render"))
    return {
        "schema_version": QT_RENDER_BRIDGE_SCHEMA_VERSION,
        "kind": "qt_render_bridge",
        "active_page_id": shell_model.get("active_page_id"),
        "desktop_plan": desktop_plan,
        "shell_render_tree": shell_tree,
        "render_contract": render_contract,
        "validation": validation,
        "snapshot": snapshot,
        "summary": {
            **shell_summary,
            "desktop_plan_ready": desktop_plan_is_ready(desktop_plan),
            "render_contract_ready": bool(render_contract.get("ready_to_render")),
            "snapshot_hash": snapshot.get("payload_hash"),
        },
        "capabilities": {
            "requires_pyside6": False,
            "opens_window": False,
            "headless_testable": True,
            "executes_commands": False,
            "local_only": True,
        },
        "ready": ready,
    }


def summarize_qt_render_bridge(bridge: Mapping[str, Any]) -> str:
    summary = _mapping(bridge.get("summary"))
    capabilities = _mapping(bridge.get("capabilities"))
    return "\n".join(
        [
            "Qt render bridge",
            f"  Active page: {bridge.get('active_page_id')}",
            f"  Ready: {bridge.get('ready')}",
            f"  Nodes: {summary.get('node_count')}",
            f"  Navigation items: {summary.get('navigation_count')}",
            f"  Sensitive nodes: {summary.get('sensitive_node_count')}",
            f"  Requires PySide6: {capabilities.get('requires_pyside6')}",
            f"  Opens window: {capabilities.get('opens_window')}",
        ]
    )


__all__ = ["QT_RENDER_BRIDGE_SCHEMA_VERSION", "build_qt_render_bridge", "summarize_qt_render_bridge"]
