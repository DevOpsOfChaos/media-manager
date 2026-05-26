"""Tests for bridge_file_ops — open, reveal, delete, rename, export, integrity, contact_sheet, web_gallery, backup, exif, watermark."""
from __future__ import annotations

import json
import zipfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from media_manager.bridge_file_ops import (
    build_parser,
    cmd_backup,
    cmd_contact_sheet,
    cmd_delete,
    cmd_exif,
    cmd_export,
    cmd_integrity,
    cmd_open,
    cmd_rename,
    cmd_reveal,
    cmd_watermark,
    cmd_web_gallery,
    main,
)


# ── helpers ──

def _stdin(payload: dict) -> StringIO:
    return StringIO(json.dumps(payload))


def _stdin_raw(raw: str) -> StringIO:
    return StringIO(raw)


# ── cmd_open ──


class TestCmdOpen:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("not json")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_open()
        assert exit_code == 1
        assert "Invalid JSON" in m.getvalue()

    def test_missing_path_returns_error(self):
        with patch("sys.stdin", _stdin({})), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_open()
        assert exit_code == 1
        assert "File not found" in m.getvalue()

    def test_nonexistent_path_returns_error(self, tmp_path):
        p = tmp_path / "nonexistent.jpg"
        payload = {"path": str(p)}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_open()
        assert exit_code == 1
        assert "File not found" in m.getvalue()

    def test_valid_file_opens(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        payload = {"path": str(f)}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("os.startfile") as mock_startfile,
        ):
            exit_code = cmd_open()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "opened"
        mock_startfile.assert_called_once_with(str(f))

    def test_oserror_returns_error(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        payload = {"path": str(f)}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stderr", new_callable=StringIO) as m,
            patch("os.startfile", side_effect=OSError("denied")),
        ):
            exit_code = cmd_open()
        assert exit_code == 1
        assert "Could not open" in m.getvalue()

    def test_unicode_path(self, tmp_path):
        f = tmp_path / "t\u00e9st_\u00fcnicode.jpg"
        f.write_text("hello")
        payload = {"path": str(f)}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("os.startfile"),
        ):
            exit_code = cmd_open()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["path"] == str(f)


# ── cmd_reveal ──


class TestCmdReveal:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("{broken")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_reveal()
        assert exit_code == 1
        assert "Invalid JSON" in m.getvalue()

    def test_nonexistent_path_returns_error(self, tmp_path):
        payload = {"path": str(tmp_path / "ghost")}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_reveal()
        assert exit_code == 1
        assert "Path not found" in m.getvalue()

    def test_directory_reveals(self, tmp_path):
        payload = {"path": str(tmp_path)}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("subprocess.run"),
        ):
            exit_code = cmd_reveal()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "revealed"

    def test_file_reveals(self, tmp_path):
        f = tmp_path / "photo.jpg"
        f.write_text("data")
        payload = {"path": str(f)}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("subprocess.run"),
        ):
            exit_code = cmd_reveal()
        assert exit_code == 0

    def test_oserror_returns_error(self, tmp_path):
        payload = {"path": str(tmp_path)}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stderr", new_callable=StringIO) as m,
            patch("subprocess.run", side_effect=OSError("fail")),
        ):
            exit_code = cmd_reveal()
        assert exit_code == 1
        assert "Could not reveal" in m.getvalue()


# ── cmd_delete ──


class TestCmdDelete:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("{{bad")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_delete()
        assert exit_code == 1
        assert "Invalid JSON" in m.getvalue()

    def test_empty_path_returns_error(self):
        with patch("sys.stdin", _stdin({})), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_delete()
        assert exit_code == 1
        assert "File not found" in m.getvalue()

    def test_nonexistent_path_returns_error(self, tmp_path):
        payload = {"path": str(tmp_path / "no_file_here.txt")}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_delete()
        assert exit_code == 1
        assert "File not found" in m.getvalue()

    def test_send2trash_deletes_file(self, tmp_path):
        f = tmp_path / "delete_me.txt"
        f.write_text("trash me")
        with (
            patch("sys.stdin", _stdin({"path": str(f)})),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("send2trash.send2trash") as mock_trash,
        ):
            exit_code = cmd_delete()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "deleted"
        mock_trash.assert_called_once_with(str(f))


# ── cmd_rename ──


class TestCmdRename:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("invalid")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_rename()
        assert exit_code == 1

    def test_missing_new_name_returns_error(self, tmp_path):
        f = tmp_path / "old.txt"
        f.write_text("data")
        with (
            patch("sys.stdin", _stdin({"path": str(f)})),
            patch("sys.stderr", new_callable=StringIO) as m,
        ):
            exit_code = cmd_rename()
        assert exit_code == 1
        assert "new_name" in m.getvalue()

    def test_missing_path_returns_error(self, tmp_path):
        with (
            patch("sys.stdin", _stdin({"new_name": "n.txt"})),
            patch("sys.stderr", new_callable=StringIO) as m,
        ):
            exit_code = cmd_rename()
        assert exit_code == 1

    def test_nonexistent_path_returns_error(self, tmp_path):
        payload = {"path": str(tmp_path / "ghost.txt"), "new_name": "n.txt"}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_rename()
        assert exit_code == 1

    def test_target_exists_returns_error(self, tmp_path):
        f = tmp_path / "old.txt"
        f.write_text("old")
        existing = tmp_path / "new.txt"
        existing.write_text("existing")
        payload = {"path": str(f), "new_name": "new.txt"}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_rename()
        assert exit_code == 1
        assert "already exists" in m.getvalue()

    def test_rename_succeeds(self, tmp_path):
        f = tmp_path / "old.txt"
        f.write_text("content")
        payload = {"path": str(f), "new_name": "renamed.txt"}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_rename()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "renamed"
        assert data["new_name"] == "renamed.txt"
        assert Path(data["new_path"]).exists()
        assert not f.exists()

    def test_rename_with_unicode(self, tmp_path):
        f = tmp_path / "r\u00e9sum\u00e9.txt"
        f.write_text("content")
        new_name = "caf\u00e9.txt"
        payload = {"path": str(f), "new_name": new_name}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_rename()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "renamed"

    def test_oserror_returns_error(self, tmp_path):
        f = tmp_path / "old.txt"
        f.write_text("content")
        with (
            patch("sys.stdin", _stdin({"path": str(f), "new_name": "new.txt"})),
            patch("sys.stderr", new_callable=StringIO) as m,
            patch.object(Path, "rename", side_effect=OSError("permission")),
        ):
            exit_code = cmd_rename()
        assert exit_code == 1
        assert "Could not rename" in m.getvalue()


# ── cmd_export ──


class TestCmdExport:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("bad")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_export()
        assert exit_code == 1

    def test_missing_source_returns_error(self, tmp_path):
        payload = {"target": str(tmp_path / "out.jpg")}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_export()
        assert exit_code == 1
        assert "Source not found" in m.getvalue()

    def test_nonexistent_source_returns_error(self, tmp_path):
        payload = {"source": str(tmp_path / "ghost.jpg"), "target": str(tmp_path / "out.jpg")}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_export()
        assert exit_code == 1

    def test_export_with_pil(self, tmp_path):
        f = tmp_path / "input.jpg"
        f.write_bytes(b"fake-jpeg")
        out = tmp_path / "output.jpg"
        mock_img = MagicMock()
        mock_img.width = 4000
        mock_img.height = 3000
        mock_img.mode = "RGB"
        mock_img.resize.return_value = mock_img

        with (
            patch("sys.stdin", _stdin({"source": str(f), "target": str(out), "width": 800})),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("PIL.Image.open", return_value=mock_img),
        ):
            exit_code = cmd_export()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "exported"
        assert data["width"] == 800

    def test_export_pillow_missing(self, tmp_path):
        f = tmp_path / "input.jpg"
        f.write_bytes(b"fake-jpeg")
        out = tmp_path / "output.jpg"
        with (
            patch("sys.stdin", _stdin({"source": str(f), "target": str(out)})),
            patch("sys.stderr", new_callable=StringIO) as m,
            patch("PIL.Image.open", side_effect=ImportError("no PIL")),
        ):
            exit_code = cmd_export()
        assert exit_code == 1
        assert "Pillow" in m.getvalue()


# ── cmd_integrity ──


class TestCmdIntegrity:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("broken")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_integrity()
        assert exit_code == 1

    def test_missing_paths_returns_error(self):
        with patch("sys.stdin", _stdin({})), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_integrity()
        assert exit_code == 1
        assert "paths" in m.getvalue()

    def test_empty_paths_returns_validation_error(self):
        with (
            patch("sys.stdin", _stdin({"paths": []})),
            patch("sys.stderr", new_callable=StringIO) as m,
        ):
            exit_code = cmd_integrity()
        assert exit_code == 1
        assert "paths" in m.getvalue()

    def test_existing_files_healthy(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("hello")
        expected_size = f.stat().st_size
        with (
            patch("sys.stdin", _stdin({"paths": [{"path": str(f), "size": expected_size}]})),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_integrity()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["healthy"] is True
        assert data["total_checked"] == 1

    def test_missing_files_reported(self, tmp_path):
        payload = {"paths": [{"path": str(tmp_path / "gone.txt"), "size": 100}]}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_integrity()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["healthy"] is False
        assert data["missing_count"] == 1
        assert len(data["missing"]) == 1

    def test_size_changed_reported(self, tmp_path):
        f = tmp_path / "b.txt"
        f.write_text("hello world")
        payload = {"paths": [{"path": str(f), "size": 99999}]}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_integrity()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["size_changed_count"] == 1
        assert data["healthy"] is False

    def test_large_paths_list(self, tmp_path):
        entries = [{"path": str(tmp_path / f"file_{i}.txt"), "size": i} for i in range(500)]
        # Create first 10 files only
        for i in range(10):
            (tmp_path / f"file_{i}.txt").write_text("x" * i)
        with (
            patch("sys.stdin", _stdin({"paths": entries})),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_integrity()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["total_checked"] == 500


# ── cmd_contact_sheet ──


class TestCmdContactSheet:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("bad")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_contact_sheet()
        assert exit_code == 1

    def test_missing_paths_returns_error(self):
        payload = {"output": "/tmp/sheet.pdf"}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_contact_sheet()
        assert exit_code == 1
        assert "paths" in m.getvalue()

    def test_missing_output_returns_error(self):
        payload = {"paths": ["/a.jpg"]}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_contact_sheet()
        assert exit_code == 1
        assert "output" in m.getvalue()

    def test_pillow_missing_returns_error(self):
        payload = {"paths": ["/a.jpg"], "output": "/tmp/out.pdf"}
        with (
            patch("sys.stdin", _stdin(payload)),
            patch("sys.stderr", new_callable=StringIO) as m,
            patch("builtins.__import__", side_effect=ImportError),  # PIL import fails
        ):
            exit_code = cmd_contact_sheet()
        assert exit_code == 1
        assert "Pillow" in m.getvalue()


# ── cmd_web_gallery ──


class TestCmdWebGallery:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("bad")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_web_gallery()
        assert exit_code == 1

    def test_missing_paths_returns_error(self):
        payload = {"output_dir": "/tmp"}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_web_gallery()
        assert exit_code == 1
        assert "paths" in m.getvalue()

    def test_missing_output_dir_returns_error(self):
        payload = {"paths": ["/a.jpg"]}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_web_gallery()
        assert exit_code == 1
        assert "output_dir" in m.getvalue()


# ── cmd_backup ──


class TestCmdBackup:
    def test_missing_app_dir_returns_error(self, monkeypatch, tmp_path):
        monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path / ".media-manager"))
        monkeypatch.delenv("MEDIA_MANAGER_HOME", raising=False)
        # Force a non-existent path
        monkeypatch.setenv("MEDIA_MANAGER_HOME", str(tmp_path / "nonexistent_dir"))
        with patch("sys.stdin", _stdin({})), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_backup()
        assert exit_code == 1
        assert "not found" in m.getvalue()

    def test_valid_backup(self, monkeypatch, tmp_path):
        app_dir = tmp_path / ".media-manager"
        app_dir.mkdir()
        (app_dir / "settings.json").write_text("{}")
        monkeypatch.setenv("MEDIA_MANAGER_HOME", str(app_dir))

        with (
            patch("sys.stdin", _stdin({})),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_backup()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "backed_up"
        backup_path = Path(data["path"])
        assert backup_path.exists()
        assert backup_path.suffix == ".zip"

    def test_backup_excludes_models_and_pycache(self, monkeypatch, tmp_path):
        app_dir = tmp_path / ".media-manager"
        app_dir.mkdir()
        (app_dir / "settings.json").write_text("{}")
        models_dir = app_dir / "models"
        models_dir.mkdir()
        (models_dir / "face_model.bin").write_bytes(b"\x00" * 100)
        pycache_dir = app_dir / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "module.pyc").write_text("")
        monkeypatch.setenv("MEDIA_MANAGER_HOME", str(app_dir))

        with (
            patch("sys.stdin", _stdin({})),
            patch("sys.stdout", new_callable=StringIO) as m,
        ):
            exit_code = cmd_backup()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        backup_path = Path(data["path"])
        with zipfile.ZipFile(backup_path, "r") as zf:
            names = zf.namelist()
        assert "settings.json" in names
        assert not any("models" in n for n in names)
        assert not any("__pycache__" in n for n in names)


# ── cmd_exif ──


class TestCmdExif:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("bad")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_exif()
        assert exit_code == 1

    def test_missing_path_returns_error(self):
        with patch("sys.stdin", _stdin({})), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_exif()
        assert exit_code == 1
        assert "File not found" in m.getvalue()

    def test_nonexistent_path_returns_error(self, tmp_path):
        payload = {"path": str(tmp_path / "ghost.jpg")}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_exif()
        assert exit_code == 1
        assert "File not found" in m.getvalue()

    def test_exif_read_success(self, tmp_path):
        f = tmp_path / "photo.jpg"
        f.write_bytes(b"jpeg-data")
        fake_meta = {
            "Model": "Canon EOS",
            "ISO": 400,
            "ImageWidth": 6000,
            "ImageHeight": 4000,
        }
        with (
            patch("sys.stdin", _stdin({"path": str(f)})),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("media_manager.exiftool.read_exiftool_metadata", return_value=(fake_meta, True, None, None)),
        ):
            exit_code = cmd_exif()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "ok"
        assert data["metadata"]["camera"] == "Canon EOS"
        assert data["metadata"]["iso"] == 400
        assert data["metadata"]["megapixels"] == 24.0

    def test_exif_read_failure(self, tmp_path):
        f = tmp_path / "photo.jpg"
        f.write_bytes(b"jpeg-data")
        with (
            patch("sys.stdin", _stdin({"path": str(f)})),
            patch("sys.stderr", new_callable=StringIO) as m,
            patch("media_manager.exiftool.read_exiftool_metadata", return_value=(None, False, "codec_error", "bad data")),
        ):
            exit_code = cmd_exif()
        assert exit_code == 1
        assert "Could not read EXIF" in m.getvalue()


# ── cmd_watermark ──


class TestCmdWatermark:
    def test_invalid_json_returns_error(self):
        with patch("sys.stdin", _stdin_raw("bad")), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_watermark()
        assert exit_code == 1

    def test_missing_source_returns_error(self, tmp_path):
        payload = {"target": str(tmp_path / "out.jpg")}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_watermark()
        assert exit_code == 1
        assert "Source not found" in m.getvalue()

    def test_nonexistent_source_returns_error(self, tmp_path):
        payload = {"source": str(tmp_path / "ghost.jpg"), "target": str(tmp_path / "out.jpg")}
        with patch("sys.stdin", _stdin(payload)), patch("sys.stderr", new_callable=StringIO) as m:
            exit_code = cmd_watermark()
        assert exit_code == 1

    def test_creates_target_parent_dir(self, tmp_path):
        f = tmp_path / "input.jpg"
        f.write_bytes(b"jpeg-data")
        out_dir = tmp_path / "nested" / "output"
        out = out_dir / "result.jpg"
        mock_img = MagicMock()
        mock_img.mode = "RGB"
        mock_img.size = (200, 100)
        mock_img.width = 200
        mock_img.height = 100
        rgba_img = MagicMock()
        rgba_img.size = (200, 100)

        with (
            patch("sys.stdin", _stdin({"source": str(f), "target": str(out), "text": "Test"})),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("PIL.Image.open", return_value=rgba_img),
            patch("PIL.Image.new", return_value=MagicMock()),
            patch("PIL.ImageDraw.Draw"),
            patch("PIL.ImageDraw.ImageDraw.textbbox", return_value=(0, 0, 100, 20)),
            patch("PIL.Image.alpha_composite", return_value=mock_img),
        ):
            exit_code = cmd_watermark()
        assert exit_code == 0
        data = json.loads(m.getvalue())
        assert data["status"] == "watermarked"
        assert out_dir.exists()

    def test_pillow_missing_returns_error(self, tmp_path):
        f = tmp_path / "input.jpg"
        f.write_bytes(b"jpeg-data")
        out = tmp_path / "out.jpg"
        with (
            patch("sys.stdin", _stdin({"source": str(f), "target": str(out)})),
            patch("sys.stderr", new_callable=StringIO) as m,
            patch("PIL.Image.open", side_effect=ImportError),
        ):
            exit_code = cmd_watermark()
        assert exit_code == 1
        assert "Pillow" in m.getvalue()

    def test_watermark_with_custom_position(self, tmp_path):
        f = tmp_path / "input.jpg"
        f.write_bytes(b"jpeg-data")
        out = tmp_path / "out.jpg"
        mock_img = MagicMock()
        mock_img.mode = "RGB"
        mock_img.size = (200, 100)
        mock_img.width = 200
        mock_img.height = 100
        rgba_img = MagicMock()
        rgba_img.size = (200, 100)
        rgba_img.mode = "RGBA"

        with (
            patch("sys.stdin", _stdin({"source": str(f), "target": str(out), "text": "Copyright", "position": "top-left", "opacity": 80})),
            patch("sys.stdout", new_callable=StringIO) as m,
            patch("PIL.Image.open", return_value=rgba_img),
            patch("PIL.Image.new", return_value=MagicMock()),
            patch("PIL.ImageDraw.Draw"),
            patch("PIL.ImageDraw.ImageDraw.textbbox", return_value=(0, 0, 100, 20)),
            patch("PIL.Image.alpha_composite", return_value=mock_img),
        ):
            exit_code = cmd_watermark()
        assert exit_code == 0


# ── parser ──


class TestParser:
    def test_all_actions_accepted(self):
        parser = build_parser()
        for action in ["open", "reveal", "delete", "rename", "exif", "export", "integrity", "backup", "contact_sheet", "web_gallery", "watermark"]:
            args = parser.parse_args([action])
            assert args.action == action

    def test_unknown_action_rejected(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["bogus"])


# ── main ──


class TestMain:
    def test_main_unknown_action_exits(self):
        with patch("sys.stderr", new_callable=StringIO):
            try:
                main(["bogus"])
                assert False
            except SystemExit as e:
                assert e.code == 2

    def test_main_no_args_exits(self):
        with patch("sys.stderr", new_callable=StringIO):
            try:
                main([])
                assert False
            except SystemExit as e:
                assert e.code == 2
