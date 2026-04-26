from __future__ import annotations

from media_manager.core.gui_qt_people_review_render_tree import build_people_review_render_tree
from media_manager.core.gui_qt_render_tree_validator import validate_render_tree


def test_people_review_render_tree_marks_face_nodes_sensitive() -> None:
    page_plan = {
        "page_id": "people-review",
        "body": {
            "kind": "qt_people_review_visible_plan",
            "page_id": "people-review",
            "layout": "master_detail_faces",
            "group_count": 1,
            "face_count": 1,
            "privacy_notice": "Face crops are sensitive local biometric data.",
            "sections": [
                {
                    "section_id": "people-review-groups",
                    "variant": "master_list",
                    "children": [
                        {
                            "kind": "people_group_button",
                            "group_id": "person-1",
                            "label": "Person 1",
                            "selected": True,
                        }
                    ],
                },
                {
                    "section_id": "people-review-detail",
                    "variant": "detail_grid",
                    "children": [
                        {
                            "kind": "people_face_card",
                            "face_id": "face-1",
                            "decision_status": "pending",
                            "asset_ref": {"path": "faces/face-1.jpg"},
                            "sensitive": True,
                        }
                    ],
                },
            ],
        },
    }

    tree = build_people_review_render_tree(page_plan)
    validation = validate_render_tree(tree["root"])

    assert tree["kind"] == "qt_people_review_render_tree"
    assert tree["summary"]["sensitive_node_count"] >= 2
    assert tree["privacy_notice"].startswith("Face crops")
    assert validation["valid"] is True
