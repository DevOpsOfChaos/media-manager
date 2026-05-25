from __future__ import annotations

import hashlib
import json
import sys
from io import StringIO
from pathlib import Path
from unittest import mock

from media_manager.bridge_duplicates_apply import cmd_apply


def test_duplicates_apply_deletes_duplicate(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    keep = source / "keep.jpg"
    dup = source / "dup.jpg"
    content = b"identical-content-for-hash"
    keep.write_bytes(content)
    dup.write_bytes(content)

    digest = hashlib.sha256(content).hexdigest()
    group_id = f"{len(content)}:{digest}"
    decisions = {group_id: str(keep)}

    payload = {
        "source_dirs": [str(source)],
        "decisions": decisions,
        "mode": "delete",
    }
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_apply()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert output["kind"] == "apply"
    assert output["executed_rows"] >= 1
    assert keep.exists()
    assert not dup.exists()


def test_duplicates_apply_reports_journal_entries(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    keep = source / "keep.jpg"
    dup = source / "dup.jpg"
    content = b"identical-content-for-hash-2"
    keep.write_bytes(content)
    dup.write_bytes(content)

    digest = hashlib.sha256(content).hexdigest()
    decisions = {f"{len(content)}:{digest}": str(keep)}

    payload = {
        "source_dirs": [str(source)],
        "decisions": decisions,
        "mode": "delete",
    }
    fake_stdin = StringIO(json.dumps(payload))
    fake_stdout = StringIO()
    with mock.patch.object(sys, "stdin", fake_stdin), mock.patch.object(sys, "stdout", fake_stdout):
        exit_code = cmd_apply()

    assert exit_code == 0
    output = json.loads(fake_stdout.getvalue())
    assert len(output["journal_entries"]) >= 1
