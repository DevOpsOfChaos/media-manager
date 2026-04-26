from __future__ import annotations

from media_manager.core.gui_qt_page_adapter import adapt_page_model_for_qt


def test_page_adapter_dispatches_table_pages() -> None:
    plan = adapt_page_model_for_qt(
        {
            "page_id": "run-history",
            "kind": "table_page",
            "title": "Runs",
            "columns": ["run_id", "status"],
            "rows": [{"run_id": "run-1", "status": "ok"}],
        }
    )

    assert plan["kind"] == "qt_generic_table_page_plan"
    assert plan["summary"]["widget_type_summary"] == {"data_table": 1}
    assert plan["widgets"][0]["total_row_count"] == 1


def test_page_adapter_dispatches_people_pages() -> None:
    plan = adapt_page_model_for_qt({"page_id": "people-review", "kind": "people_review_page", "groups": []})

    assert plan["page_id"] == "people-review"
    assert plan["layout"] == "people_review_master_detail"
    assert plan["summary"]["widget_count"] >= 3
