from __future__ import annotations

from media_manager.core.gui_layout import build_layout_tokens, build_page_layout, normalize_density


def test_layout_tokens_support_density() -> None:
    assert normalize_density("compact") == "compact"
    assert normalize_density("unknown") == "comfortable"
    tokens = build_layout_tokens("spacious")
    assert tokens["density"] == "spacious"
    assert tokens["tokens"]["padding"] > 20


def test_people_review_layout_is_master_detail() -> None:
    layout = build_page_layout("people-review")
    assert layout["layout"] == "master_detail_gallery"
