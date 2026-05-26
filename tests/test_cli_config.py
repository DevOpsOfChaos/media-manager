from __future__ import annotations

import json
from pathlib import Path

from media_manager import cli_config


def test_config_set_get(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    result = cli_config.main(["--set", "language", "--value", "de"])
    assert result == 0
    capsys.readouterr()

    result = cli_config.main(["--get", "language"])
    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.strip() == "de"


def test_config_show(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    cli_config.main(["--set", "language", "--value", "de"])
    capsys.readouterr()

    result = cli_config.main(["--show"])
    captured = capsys.readouterr()
    assert result == 0
    assert "language" in captured.out


def test_config_show_empty(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    result = cli_config.main(["--show"])
    captured = capsys.readouterr()
    assert result == 0
    assert "No configuration found" in captured.out


def test_config_get_with_default(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    result = cli_config.main(["--get", "missing", "--default", "fallback"])
    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.strip() == "fallback"


def test_config_unset(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    cli_config.main(["--set", "language", "--value", "de"])
    capsys.readouterr()

    result = cli_config.main(["--unset", "language"])
    captured = capsys.readouterr()
    assert result == 0
    assert "Removed" in captured.out

    result = cli_config.main(["--get", "language"])
    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.strip() == ""


def test_config_reset(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    cli_config.main(["--set", "language", "--value", "de"])
    capsys.readouterr()
    assert config_file.exists()

    result = cli_config.main(["--reset"])
    captured = capsys.readouterr()
    assert result == 0
    assert not config_file.exists()


def test_config_json_output(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    cli_config.main(["--set", "language", "--value", "de"])
    capsys.readouterr()

    result = cli_config.main(["--get", "language", "--json"])
    captured = capsys.readouterr()
    assert result == 0
    data = json.loads(captured.out)
    assert data["key"] == "language"
    assert data["value"] == "de"
    assert data["found"] is True


def test_config_set_without_value(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    result = cli_config.main(["--set", "key"])
    captured = capsys.readouterr()
    assert result == 1
    assert "Error" in captured.err


def test_config_default_show_when_no_args(tmp_path: Path, monkeypatch, capsys) -> None:
    config_file = tmp_path / "config.json"
    monkeypatch.setattr(cli_config, "CONFIG_PATH", config_file)

    result = cli_config.main([])
    captured = capsys.readouterr()
    assert result == 0
