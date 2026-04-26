from media_manager.core.gui_devtools_model import build_devtools_panel, build_model_schema_summary


def test_devtools_summary_lists_fields() -> None:
    summary = build_model_schema_summary({"title": "X", "items": [1, 2]}, model_name="page")
    assert summary["field_count"] == 2
    assert next(field for field in summary["fields"] if field["name"] == "items")["type"] == "array"


def test_devtools_panel_is_exportable() -> None:
    panel = build_devtools_panel({"page": {"title": "X"}, "shell": {"active": True}})
    assert panel["model_count"] == 2
    assert panel["exportable"] is True
