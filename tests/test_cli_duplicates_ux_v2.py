from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from media_manager.cli_duplicates import _build_decision_rows, main
from media_manager.cleanup_plan import UnresolvedExactGroup
from media_manager.duplicates import ExactDuplicateGroup


def _group(tmp_path: Path, name_a: str = "keep.jpg", name_b: str = "remove.jpg", digest: str = "digest") -> ExactDuplicateGroup:
    a = tmp_path / name_a
    b = tmp_path / name_b
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    return ExactDuplicateGroup(
        files=[a, b],
        file_size=1,
        sample_digest="sample",
        full_digest=digest,
        same_name=False,
        same_suffix=True,
    )


def test_build_decision_rows_tracks_origin_and_unresolved_groups(tmp_path: Path) -> None:
    first = _group(tmp_path, digest="one")
    second = _group(tmp_path, name_a="keep2.jpg", name_b="remove2.jpg", digest="two")
    session_restore = SimpleNamespace(status="matched", decisions={"1:one": str(first.files[0])})
    decisions = {"1:one": str(first.files[0])}

    rows = _build_decision_rows([first, second], decisions, session_restore)

    assert rows[0]["origin"] == "session"
    assert rows[0]["status"] == "decided"
    assert rows[1]["status"] == "unresolved"
    assert rows[1]["origin"] is None


def test_cli_duplicates_prints_decisions_and_unresolved_groups(monkeypatch, capsys, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    group = _group(source)

    monkeypatch.setattr(
        "media_manager.cli_duplicates.scan_exact_duplicates",
        lambda config: SimpleNamespace(
            scanned_files=2,
            size_candidate_files=2,
            hashed_files=2,
            exact_groups=[group],
            exact_duplicate_files=2,
            exact_duplicates=1,
            errors=0,
            size_group_errors=0,
            sample_errors=0,
            hash_errors=0,
            compare_errors=0,
        ),
    )
    monkeypatch.setattr(
        "media_manager.cli_duplicates.build_duplicate_workflow_bundle",
        lambda exact_groups, decisions, mode, target_root=None: SimpleNamespace(
            decisions=decisions,
            cleanup_plan=SimpleNamespace(
                resolved_groups=0,
                unresolved_groups=1,
                planned_removals=[],
                estimated_reclaimable_bytes=0,
                unresolved=[UnresolvedExactGroup(group_id="1:digest", candidate_paths=group.files, file_size=1)],
            ),
            dry_run=SimpleNamespace(ready=False, planned_count=0, blocked_count=2, delete_count=0, exclude_from_copy_count=0, exclude_from_move_count=0),
            execution_preview=SimpleNamespace(ready=False, executable_count=0, deferred_count=0, blocked_count=2, delete_count=0),
        ),
    )

    code = main(["--source", str(source), "--show-decisions", "--show-unresolved"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Decision rows:" in output
    assert "[unresolved] 1:digest" in output
    assert "[Unresolved Group] 1:digest" in output
