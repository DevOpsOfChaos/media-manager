from __future__ import annotations

from pathlib import Path

from media_manager.cli_watch import main, build_parser


def test_watch_nonexistent(tmp_path: Path, capsys) -> None:
    result = main(["--source", str(tmp_path / "nope")])
    captured = capsys.readouterr()
    assert result == 1
    assert "source directory not found" in captured.err


def test_watch_parser_required_source() -> None:
    parser = build_parser()
    args = parser.parse_args(["--source", "/some/path"])
    assert args.source == Path("/some/path")


def test_watch_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["--source", "/some/path"])
    assert args.target is None
    assert args.interval == 5
    assert args.non_recursive is False
    assert args.include_hidden is False
    assert args.move is False


def test_watch_parser_full_args() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "--source", "/src",
            "--target", "/tgt",
            "--pattern", "{year}/{month}",
            "--interval", "10",
            "--move",
            "--non-recursive",
            "--include-hidden",
        ]
    )
    assert args.source == Path("/src")
    assert args.target == Path("/tgt")
    assert args.pattern == "{year}/{month}"
    assert args.interval == 10
    assert args.move is True
    assert args.non_recursive is True
    assert args.include_hidden is True
