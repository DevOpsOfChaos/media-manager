from media_manager.core.gui_qt_table_visible_plan import build_qt_table_visible_plan, table_plan_has_rows


def test_table_visible_plan_normalizes_cells() -> None:
    plan = build_qt_table_visible_plan(
        table_id="runs",
        columns=["run_id", "path"],
        rows=[{"run_id": "r1", "path": {"path": "C:/run"}}],
    )
    assert plan["column_count"] == 2
    assert plan["rows"][0]["cells"][1]["text"] == "C:/run"
    assert table_plan_has_rows(plan)


def test_table_visible_plan_empty_state() -> None:
    plan = build_qt_table_visible_plan(table_id="empty", rows=[])
    assert plan["empty_state"]["visible"] is True
    assert not table_plan_has_rows(plan)
