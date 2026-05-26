from __future__ import annotations

from pathlib import Path

from media_manager.cli_stats import main


def test_stats_basic(tmp_path: Path, capsys) -> None:
    source = tmp_path / "photos"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"x" * 100)
    (source / "b.png").write_bytes(b"x" * 200)
    (source / "c.mp4").write_bytes(b"x" * 300)

    result = main(["--source", str(source)])
    assert result == 0

    captured = capsys.readouterr()
    assert "Total files: 3" in captured.out


def test_stats_json(tmp_path: Path, capsys) -> None:
    source = tmp_path / "photos"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"x")

    result = main(["--source", str(source), "--json"])
    captured = capsys.readouterr()
    assert result == 0
    assert "jpg" in captured.out


def test_stats_json_env(tmp_path: Path, capsys, monkeypatch) -> None:
    source = tmp_path / "photos"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"x")

    monkeypatch.setenv("MEDIA_MANAGER_JSON", "1")
    result = main(["--source", str(source)])
    captured = capsys.readouterr()
    assert result == 0
    assert "jpg" in captured.out


def test_stats_nonexistent(tmp_path: Path, capsys) -> None:
    result = main(["--source", str(tmp_path / "nope")])
    captured = capsys.readouterr()
    assert result == 1
    assert "does not exist" in captured.err


def test_stats_non_recursive(tmp_path: Path, capsys) -> None:
    source = tmp_path / "photos"
    source.mkdir()
    sub = source / "sub"
    sub.mkdir()
    (source / "top.jpg").write_bytes(b"x")
    (sub / "deep.jpg").write_bytes(b"x")

    result = main(["--source", str(source), "--non-recursive"])
    captured = capsys.readouterr()
    assert result == 0
    assert "Total files: 1" in captured.out


def test_stats_top_limit(tmp_path: Path, capsys) -> None:
    source = tmp_path / "photos"
    source.mkdir()
    (source / "a.jpg").write_bytes(b"x")
    (source / "b.png").write_bytes(b"x")

    result = main(["--source", str(source), "--top", "1"])
    captured = capsys.readouterr()
    assert result == 0
    assert "Total files: 2" in captured.out
