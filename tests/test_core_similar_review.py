from __future__ import annotations

import os
import time
from pathlib import Path

from media_manager.similar_images import SimilarImageGroup, SimilarImageMember
from media_manager.similar_review import build_similar_review_report, choose_similar_keep_path


def _member(path: Path, hash_hex: str, distance: int = 0) -> SimilarImageMember:
    return SimilarImageMember(path=path, hash_hex=hash_hex, distance=distance)


def test_choose_similar_keep_path_supports_first_newest_and_oldest(tmp_path: Path) -> None:
    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    third = tmp_path / "third.jpg"
    first.write_bytes(b"1")
    second.write_bytes(b"2")
    third.write_bytes(b"3")

    now = time.time()
    os.utime(first, (now - 30, now - 30))
    os.utime(second, (now - 20, now - 20))
    os.utime(third, (now - 10, now - 10))

    group = SimilarImageGroup(
        anchor_path=first,
        members=[
            _member(first, "0f"),
            _member(second, "0e", distance=1),
            _member(third, "0d", distance=2),
        ],
    )

    assert choose_similar_keep_path(group, "first") == first
    assert choose_similar_keep_path(group, "newest") == third
    assert choose_similar_keep_path(group, "oldest") == first


def test_build_similar_review_report_marks_one_keep_and_rest_review_candidates(tmp_path: Path) -> None:
    keep = tmp_path / "keep.jpg"
    candidate = tmp_path / "candidate.jpg"
    keep.write_bytes(b"1")
    candidate.write_bytes(b"2")

    group = SimilarImageGroup(
        anchor_path=keep,
        members=[
            _member(keep, "0f"),
            _member(candidate, "0e", distance=1),
        ],
    )

    report = build_similar_review_report([group], keep_policy="first")

    assert report.group_count == 1
    assert report.row_count == 2
    assert report.keep_count == 1
    assert report.review_candidate_count == 1
    keep_row = next(item for item in report.rows if item.status == "keep")
    candidate_row = next(item for item in report.rows if item.status == "review-candidate")
    assert keep_row.path == keep
    assert keep_row.distance_to_keep == 0
    assert candidate_row.recommended_keep_path == keep
    assert candidate_row.distance_to_keep == 1
