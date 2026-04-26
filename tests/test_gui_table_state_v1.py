from __future__ import annotations

from media_manager.core.gui_table_state import build_table_state, filter_table_rows, sort_table_rows


def test_filter_table_rows_by_query_and_status() -> None:
    rows = [{"name": "Alice", "status": "ok"}, {"name": "Bob", "status": "error"}]

    assert filter_table_rows(rows, query="bo", status_filter="error") == [{"name": "Bob", "status": "error"}]


def test_sort_table_rows_by_key() -> None:
    rows = [{"name": "Bob"}, {"name": "Alice"}]

    assert [row["name"] for row in sort_table_rows(rows, sort_key="name")] == ["Alice", "Bob"]


def test_build_table_state_truncates() -> None:
    state = build_table_state(table_id="x", columns=["name"], rows=[{"name": "a"}, {"name": "b"}], limit=1)

    assert state["returned_row_count"] == 1
    assert state["truncated"] is True
