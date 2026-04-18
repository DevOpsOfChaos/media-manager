from __future__ import annotations

import subprocess
from pathlib import Path

from media_manager.exiftool import read_exiftool_metadata, resolve_exiftool_path



def test_resolve_exiftool_path_accepts_directory_input(tmp_path: Path) -> None:
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    candidate = tool_dir / "exiftool(-k).exe"
    candidate.write_text("stub", encoding="utf-8")

    resolved = resolve_exiftool_path(tool_dir)

    assert resolved == candidate



def test_read_exiftool_metadata_reports_timeout(monkeypatch, tmp_path: Path) -> None:
    media_file = tmp_path / "photo.jpg"
    media_file.write_bytes(b"jpg")
    tool = tmp_path / "exiftool.exe"
    tool.write_text("stub", encoding="utf-8")

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=kwargs.get("args", "exiftool"), timeout=20)

    monkeypatch.setattr("subprocess.run", _raise_timeout)

    metadata, available, error_kind, error = read_exiftool_metadata(media_file, exiftool_path=tool)

    assert metadata is None
    assert available is True
    assert error_kind == "timeout"
    assert error is not None
