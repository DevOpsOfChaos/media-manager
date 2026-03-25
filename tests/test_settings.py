from media_manager.settings import get_import_set, list_import_sets, remove_import_set, upsert_import_set


def test_upsert_import_set_normalizes_and_sorts() -> None:
    data = {}
    updated = upsert_import_set(
        data,
        " Trip ",
        ["C:/Photos/A", "C:/Photos/A", "", "C:/Photos/B"],
        "D:/Sorted",
        "",
    )

    assert list_import_sets(updated) == [
        {
            "name": "Trip",
            "source_dirs": ["C:/Photos/A", "C:/Photos/B"],
            "target_dir": "D:/Sorted",
            "target_template": "{year}/{month}",
        }
    ]


def test_upsert_import_set_replaces_existing_name_case_insensitively() -> None:
    data = upsert_import_set({}, "Trip", ["C:/A"], "D:/One", "{year}")
    updated = upsert_import_set(data, "trip", ["C:/B"], "D:/Two", "{year}/{month}")

    assert list_import_sets(updated) == [
        {
            "name": "trip",
            "source_dirs": ["C:/B"],
            "target_dir": "D:/Two",
            "target_template": "{year}/{month}",
        }
    ]


def test_get_and_remove_import_set() -> None:
    data = upsert_import_set({}, "Trip", ["C:/A"], "D:/One", "{year}")
    assert get_import_set(data, "TRIP") == {
        "name": "Trip",
        "source_dirs": ["C:/A"],
        "target_dir": "D:/One",
        "target_template": "{year}",
    }

    cleaned = remove_import_set(data, "trip")
    assert list_import_sets(cleaned) == []
