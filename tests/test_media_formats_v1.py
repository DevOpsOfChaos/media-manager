from media_manager.media_formats import (
    get_media_format_capability,
    is_supported_exact_duplicate_extension,
    is_supported_media_extension,
    is_supported_similar_image_extension,
    list_supported_media_extensions,
    list_supported_similar_image_extensions,
)


def test_media_capabilities_distinguish_exact_and_similarity_support() -> None:
    heic = get_media_format_capability(".heic")
    jpg = get_media_format_capability("jpg")
    mov = get_media_format_capability(".mov")

    assert heic is not None
    assert heic.exact_duplicates is True
    assert heic.similar_images is False

    assert jpg is not None
    assert jpg.exact_duplicates is True
    assert jpg.similar_images is True

    assert mov is not None
    assert mov.exact_duplicates is True
    assert mov.similar_images is False


def test_supported_media_extensions_include_common_legacy_aliases() -> None:
    extensions = list_supported_media_extensions()

    assert ".jfif" in extensions
    assert ".jpe" in extensions
    assert ".m4v" in extensions
    assert ".mpeg" in extensions

    assert is_supported_media_extension(".jfif") is True
    assert is_supported_exact_duplicate_extension(".m4v") is True
    assert is_supported_similar_image_extension(".jfif") is True
    assert ".heic" not in list_supported_similar_image_extensions()
