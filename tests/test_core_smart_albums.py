from __future__ import annotations

from media_manager.core.smart_albums import suggest_albums


def _make_meta(camera_model: str | None = None, date_str: str | None = None) -> dict:
    meta: dict = {"camera": {}, "shot": {}}
    if camera_model:
        meta["camera"]["model"] = camera_model
    if date_str:
        meta["shot"]["datetime"] = date_str
    return meta


class TestSuggestAlbumsDateClusters:
    def test_single_cluster(self) -> None:
        files = [_make_meta(date_str=f"2024:07:{d:02d} 12:00:00") for d in range(1, 16)]
        suggestions = suggest_albums(files)
        date_clusters = [s for s in suggestions if s["type"] == "date_cluster"]
        assert len(date_clusters) == 1
        assert date_clusters[0]["file_count"] == 15
        assert date_clusters[0]["confidence"] == 0.7

    def test_multiple_clusters(self) -> None:
        dates_june = [_make_meta(date_str=f"2024:06:{d:02d} 12:00:00") for d in range(1, 9)]
        dates_august = [_make_meta(date_str=f"2024:08:{d:02d} 12:00:00") for d in range(10, 18)]
        files = dates_june + dates_august
        suggestions = suggest_albums(files)
        date_clusters = [s for s in suggestions if s["type"] == "date_cluster"]
        assert len(date_clusters) >= 2

    def test_skip_small_clusters(self) -> None:
        files = [_make_meta(date_str=f"2024:07:{d:02d} 12:00:00") for d in range(1, 5)]
        suggestions = suggest_albums(files)
        date_clusters = [s for s in suggestions if s["type"] == "date_cluster"]
        assert len(date_clusters) == 0

    def test_adjacent_dates_same_cluster(self) -> None:
        files = [_make_meta(date_str=f"2024:07:{d:02d} 12:00:00") for d in range(1, 16)]
        suggestions = suggest_albums(files)
        date_clusters = [s for s in suggestions if s["type"] == "date_cluster"]
        assert len(date_clusters) == 1

    def test_ignore_invalid_dates(self) -> None:
        files = (
            [_make_meta(date_str=f"2024:07:{d:02d} 12:00:00") for d in range(1, 13)]
            + [_make_meta(date_str="not-a-date"), _make_meta(date_str="")]
        )
        suggestions = suggest_albums(files)
        date_clusters = [s for s in suggestions if s["type"] == "date_cluster"]
        assert len(date_clusters) == 1
        assert date_clusters[0]["file_count"] == 12


class TestSuggestAlbumsCamera:
    def test_popular_camera(self) -> None:
        files = [_make_meta(camera_model="Canon EOS R5") for _ in range(15)]
        suggestions = suggest_albums(files)
        camera_clusters = [s for s in suggestions if s["type"] == "camera"]
        assert len(camera_clusters) == 1
        assert camera_clusters[0]["camera"] == "Canon EOS R5"
        assert camera_clusters[0]["file_count"] == 15
        assert camera_clusters[0]["confidence"] == 0.8

    def test_multiple_cameras(self) -> None:
        files = (
            [_make_meta(camera_model="Canon EOS R5") for _ in range(15)]
            + [_make_meta(camera_model="Sony A7IV") for _ in range(12)]
            + [_make_meta(camera_model="iPhone 14") for _ in range(5)]
        )
        suggestions = suggest_albums(files)
        camera_clusters = [s for s in suggestions if s["type"] == "camera"]
        assert len(camera_clusters) == 2
        assert camera_clusters[0]["camera"] == "Canon EOS R5"
        assert camera_clusters[1]["camera"] == "Sony A7IV"

    def test_camera_below_threshold(self) -> None:
        files = [_make_meta(camera_model="Canon EOS R5") for _ in range(8)]
        suggestions = suggest_albums(files)
        camera_clusters = [s for s in suggestions if s["type"] == "camera"]
        assert len(camera_clusters) == 0

    def test_no_camera_meta(self) -> None:
        files = [_make_meta(date_str="2024:07:15 12:00:00") for _ in range(20)]
        suggestions = suggest_albums(files)
        camera_clusters = [s for s in suggestions if s["type"] == "camera"]
        assert len(camera_clusters) == 0


class TestSuggestAlbumsEmpty:
    def test_empty_input(self) -> None:
        suggestions = suggest_albums([])
        assert suggestions == []

    def test_no_usable_metadata(self) -> None:
        files = [{}, {"camera": {}}, {"shot": {}}]
        suggestions = suggest_albums(files)
        assert suggestions == []
