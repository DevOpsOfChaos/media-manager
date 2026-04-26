from media_manager.core.gui_visual_tokens import build_visual_tokens, compact_visual_token_summary, normalize_density


def test_visual_tokens_include_palette_and_legacy_tokens() -> None:
    tokens = build_visual_tokens(theme_payload={"theme": "modern-light", "palette": {"background": "#fff", "accent": "#00f"}}, density="compact")

    assert tokens["density"] == "compact"
    assert tokens["palette"]["background"] == "#fff"
    assert tokens["tokens"] == tokens["palette"]
    assert tokens["component"]["sidebar_width"] < build_visual_tokens(density="spacious")["component"]["sidebar_width"]
    assert compact_visual_token_summary(tokens)["has_background"] is True


def test_normalize_density_defaults_to_comfortable() -> None:
    assert normalize_density("unknown") == "comfortable"
