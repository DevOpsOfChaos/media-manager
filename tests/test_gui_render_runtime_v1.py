from media_manager.core.gui_render_runtime import build_render_runtime, flatten_widget_tree, summarize_render_contract


def test_render_runtime_flattens_widget_tree() -> None:
    spec = {"id": "root", "type": "section", "children": [{"id": "title", "type": "text"}]}

    flat = flatten_widget_tree(spec)
    summary = summarize_render_contract({"root": spec})

    assert [item["id"] for item in flat] == ["root", "title"]
    assert summary["widget_count"] == 2
    assert summary["type_summary"]["section"] == 1


def test_render_runtime_reports_empty_contract() -> None:
    runtime = build_render_runtime({})

    assert runtime["summary"]["widget_count"] == 0
    assert runtime["root_widget_id"] is None
    assert runtime["summary"]["diagnostics"][0]["code"] == "empty_render_contract"
