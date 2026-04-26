from media_manager.core.gui_image_loading_model import build_image_load_request, build_image_loading_queue


def test_image_load_request_reports_missing() -> None:
    request = build_image_load_request({"path": "missing.jpg", "role": "face"})

    assert request["status"] == "missing"
    assert request["priority"] == 50


def test_image_loading_queue_sorts_existing_first(tmp_path) -> None:
    image = tmp_path / "face.jpg"
    image.write_bytes(b"x")
    queue = build_image_loading_queue([{"path": "missing.jpg"}, {"path": str(image)}])

    assert queue["request_count"] == 2
    assert queue["requests"][0]["status"] == "ready"
    assert queue["missing_count"] == 1
