from __future__ import annotations

import json
from datetime import datetime, timedelta
from io import StringIO
import sys
from unittest import mock

from media_manager.core.smart_albums import suggest_albums


def test_suggest_date_clusters() -> None:
    files_meta = []
    base = datetime(2024, 6, 1)
    for i in range(15):
        files_meta.append({"shot": {"datetime": (base + timedelta(days=i)).strftime("%Y:%m:%d %H:%M:%S")}})

    result = suggest_albums(files_meta)
    date_clusters = [s for s in result if s["type"] == "date_cluster"]
    assert len(date_clusters) == 1
    assert date_clusters[0]["file_count"] == 15
    assert date_clusters[0]["confidence"] == 0.7


def test_suggest_date_clusters_with_gap() -> None:
    files_meta = []
    base = datetime(2024, 6, 1)
    for i in range(6):
        files_meta.append({"shot": {"datetime": (base + timedelta(days=i)).strftime("%Y:%m:%d %H:%M:%S")}})
    for i in range(6):
        files_meta.append({"shot": {"datetime": (base + timedelta(days=20 + i)).strftime("%Y:%m:%d %H:%M:%S")}})

    result = suggest_albums(files_meta)
    date_clusters = [s for s in result if s["type"] == "date_cluster"]
    assert len(date_clusters) == 2


def test_suggest_small_cluster_ignored() -> None:
    files_meta = [
        {"shot": {"datetime": "2024:06:01 10:00:00"}},
        {"shot": {"datetime": "2024:06:02 10:00:00"}},
    ]
    result = suggest_albums(files_meta)
    date_clusters = [s for s in result if s["type"] == "date_cluster"]
    assert len(date_clusters) == 0


def test_suggest_camera_groups() -> None:
    files_meta = []
    for _ in range(12):
        files_meta.append({"camera": {"model": "Canon EOS R5"}})
    for _ in range(5):
        files_meta.append({"camera": {"model": "Sony A7S3"}})

    result = suggest_albums(files_meta)
    camera_clusters = [s for s in result if s["type"] == "camera"]
    assert len(camera_clusters) == 1
    assert camera_clusters[0]["camera"] == "Canon EOS R5"
    assert camera_clusters[0]["file_count"] == 12


def test_suggest_empty_input() -> None:
    result = suggest_albums([])
    assert result == []


def test_bridge_suggest(tmp_path) -> None:
    from media_manager.bridge_smart_albums import cmd_suggest

    files_meta = [{"shot": {"datetime": "2024:06:01 10:00:00"}} for _ in range(10)]

    fake_stdin = StringIO(json.dumps({"files_meta": files_meta}))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_suggest()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert "suggestions" in output
    assert isinstance(output["suggestions"], list)
