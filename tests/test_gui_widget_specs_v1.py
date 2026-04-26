from media_manager.core.gui_widget_specs import build_card_spec, build_table_spec, build_widget_spec, summarize_widget_tree


def test_widget_tree_summary_counts_nested_widgets() -> None:
    root = build_widget_spec(
        "root",
        "section",
        children=[
            build_card_spec("a", "A"),
            build_table_spec("t", columns=["name"], rows=[{"name": "Jane"}]),
        ],
    )

    summary = summarize_widget_tree(root)

    assert summary["widget_count"] == 3
    assert summary["type_summary"]["card"] == 1
    assert summary["type_summary"]["table"] == 1
