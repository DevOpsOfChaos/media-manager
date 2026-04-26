from __future__ import annotations

from media_manager.core.gui_qt_render_tree import build_render_node, summarize_render_tree
from media_manager.core.gui_qt_render_tree_validator import render_tree_is_safe, validate_render_tree


def test_render_tree_summary_counts_nodes_roles_and_sensitive_flags() -> None:
    root = build_render_node(
        "root",
        "ShellFrame",
        role="application_shell",
        children=[
            build_render_node("nav", "NavigationRail", role="navigation"),
            build_render_node("face-1", "FaceCard", role="people_face", sensitive=True),
        ],
    )

    summary = summarize_render_tree(root)

    assert summary["node_count"] == 3
    assert summary["sensitive_node_count"] == 1
    assert summary["component_summary"]["FaceCard"] == 1
    assert render_tree_is_safe(root) is True


def test_render_tree_validator_rejects_duplicate_ids_and_immediate_execution() -> None:
    root = build_render_node(
        "root",
        "ShellFrame",
        children=[
            build_render_node("dup", "Button"),
            build_render_node("dup", "Button", executes_immediately=True),
        ],
    )

    validation = validate_render_tree(root)

    assert validation["valid"] is False
    assert "duplicate_node_id:dup" in validation["errors"]
    assert "node_executes_immediately:dup" in validation["errors"]
