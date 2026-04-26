from __future__ import annotations

from media_manager.core.gui_qt_render_tree import build_render_node
from media_manager.core.gui_qt_render_tree_snapshot import build_render_tree_snapshot, compare_render_tree_snapshots


def test_render_tree_snapshot_is_deterministic_and_diffable() -> None:
    root = build_render_node(
        "root",
        "ShellFrame",
        children=[build_render_node("page", "DashboardPage", props={"page_id": "dashboard"})],
    )

    first = build_render_tree_snapshot(root)
    second = build_render_tree_snapshot(root)
    diff = compare_render_tree_snapshots(first, second)

    assert first["payload_hash"] == second["payload_hash"]
    assert first["node_count"] == 2
    assert diff["same_hash"] is True
    assert diff["node_count_delta"] == 0
