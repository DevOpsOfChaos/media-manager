from media_manager.core.gui_table_renderer import build_table_render_spec, table_columns_from_rows


def test_table_renderer_builds_widget_spec() -> None:
    rows = [{"name": "Jane", "status": "ok"}]
    spec = build_table_render_spec({"columns": table_columns_from_rows(rows), "rows": rows}, table_id="people")

    assert spec["summary"]["row_count"] == 1
    assert spec["widget"]["widget_type"] == "table"
    assert spec["interactions"]["supports_search"] is True
