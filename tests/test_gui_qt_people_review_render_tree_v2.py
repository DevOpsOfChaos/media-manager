from __future__ import annotations

from media_manager.core.gui_qt_people_review_render_tree import build_people_review_render_tree
from media_manager.core.gui_qt_runtime_widget_plan import build_qt_runtime_widget_plan, summarize_runtime_widget_plan


def test_people_review_render_tree_marks_page_sensitive_without_visible_faces() -> None:
    page_plan = {
        "page_id": "people-review",
        "body": {
            "kind": "qt_people_review_visible_plan",
            "page_id": "people-review",
            "layout": "master_detail_faces",
            "group_count": 1,
            "face_count": 0,
            "sections": [],
        },
    }

    tree = build_people_review_render_tree(page_plan)
    runtime_plan = build_qt_runtime_widget_plan(tree["root"])
    runtime_summary = summarize_runtime_widget_plan(runtime_plan)

    assert tree["root"]["sensitive"] is True
    assert tree["summary"]["sensitive_node_count"] >= 1
    assert runtime_summary["sensitive_node_count"] >= 1
