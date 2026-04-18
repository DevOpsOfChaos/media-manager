from __future__ import annotations

import json
from pathlib import Path

from media_manager.cli_duplicates import main
from media_manager.similar_images import SimilarImageGroup, SimilarImageMember, SimilarImageScanResult


def _similar_result(tmp_path: Path) -> SimilarImageScanResult:
    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    first.write_bytes(b"1")
    second.write_bytes(b"2")
    return SimilarImageScanResult(
        scanned_files=2,
        image_files=2,
        hashed_files=2,
        similar_pairs=1,
        similar_groups=[
            SimilarImageGroup(
                anchor_path=first,
                members=[
                    SimilarImageMember(path=first, hash_hex="0f", distance=0),
                    SimilarImageMember(path=second, hash_hex="0e", distance=1),
                ],
            )
        ],
        errors=0,
    )


def test_main_prints_similar_review_output(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")

    monkeypatch.setattr(
        "media_manager.cli_duplicates.scan_similar_images",
        lambda config: _similar_result(source),
    )

    exit_code = main(
        [
            "--source",
            str(source),
            "--similar-images",
            "--show-similar-review",
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "[Similar Review Group 1]" in out
    assert "review-candidate" in out


def test_json_report_contains_similar_review_block(monkeypatch, tmp_path: Path, capsys) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "one.jpg").write_bytes(b"duplicate-bytes")
    (source / "two.jpg").write_bytes(b"duplicate-bytes")
    report_path = tmp_path / "duplicates-report.json"

    monkeypatch.setattr(
        "media_manager.cli_duplicates.scan_similar_images",
        lambda config: _similar_result(source),
    )

    exit_code = main(
        [
            "--source",
            str(source),
            "--similar-images",
            "--json-report",
            str(report_path),
        ]
    )
    capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["similar_review"]["group_count"] == 1
    assert payload["similar_review"]["review_candidate_count"] == 1
