from media_manager.core.gui_qt_table_adapter import build_qt_table_adapter, infer_table_columns, table_adapter_summary


def test_table_adapter_builds_matrix_and_summary() -> None:
    rows = [{"name": "A", "status": "ok"}, {"name": "B", "status": "warn"}]
    assert infer_table_columns(rows, preferred=["status"])[0] == "status"
    adapter = build_qt_table_adapter(rows=rows, columns=["name", "status"], max_rows=1)
    assert adapter["visible_row_count"] == 1
    assert adapter["truncated"] is True
    assert adapter["matrix"] == [["A", "ok"]]
    assert "1/2 rows" in table_adapter_summary(adapter)
