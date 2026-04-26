from media_manager.core.gui_breadcrumbs import build_breadcrumbs, normalize_page_id


def test_build_breadcrumbs_supports_alias_and_detail() -> None:
    payload = build_breadcrumbs("people", detail_label="Max", language="de")
    assert payload["active_page_id"] == "people-review"
    assert payload["depth"] == 3
    assert payload["trail"][0] == "Übersicht"
    assert payload["trail"][-1] == "Max"


def test_normalize_page_id_maps_runs_alias() -> None:
    assert normalize_page_id("runs") == "run-history"
