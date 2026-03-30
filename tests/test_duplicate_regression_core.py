from __future__ import annotations

from pathlib import Path

from media_manager.duplicates import (
    _build_exact_group,
    _group_by_size,
    _sample_offsets,
    compute_full_hash,
    compute_sample_fingerprint,
    files_are_identical,
)


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def test_sample_offsets_for_small_and_large_files() -> None:
    assert _sample_offsets(1024, 512) == [0]

    offsets = _sample_offsets(4096, 512)
    assert len(offsets) == 3
    assert offsets[0] == 0
    assert len(set(offsets)) == 3


def test_fingerprint_hash_and_identity_helpers(tmp_path: Path) -> None:
    payload = (b"HEADER" * 20000) + (b"MIDDLE" * 20000) + (b"FOOTER" * 20000)
    different_payload = b"X" * len(payload)

    file_a = tmp_path / "a" / "IMG_0001.JPG"
    file_b = tmp_path / "b" / "IMG_0002.JPG"
    file_c = tmp_path / "c" / "IMG_0003.JPG"

    _write_bytes(file_a, payload)
    _write_bytes(file_b, payload)
    _write_bytes(file_c, different_payload)

    assert compute_sample_fingerprint(file_a) == compute_sample_fingerprint(file_b)
    assert compute_sample_fingerprint(file_a) != compute_sample_fingerprint(file_c)

    assert compute_full_hash(file_a) == compute_full_hash(file_b)
    assert compute_full_hash(file_a) != compute_full_hash(file_c)

    assert files_are_identical(file_a, file_b)
    assert not files_are_identical(file_a, file_c)


def test_group_by_size_and_exact_group_metadata(tmp_path: Path) -> None:
    payload = b"abc123" * 5000

    file_a = tmp_path / "a" / "IMG_0001.JPG"
    file_b = tmp_path / "b" / "IMG_0001.JPG"
    file_c = tmp_path / "c" / "IMG_0002.JPG"

    _write_bytes(file_a, payload)
    _write_bytes(file_b, payload)
    _write_bytes(file_c, payload)

    grouped = _group_by_size([file_a, file_b, file_c])
    assert len(grouped[file_a.stat().st_size]) == 3

    exact_group = _build_exact_group(
        [file_c, file_a, file_b],
        file_a.stat().st_size,
        compute_sample_fingerprint(file_a),
        compute_full_hash(file_a),
    )

    assert exact_group.files[0].name == "IMG_0001.JPG"
    assert exact_group.same_suffix is True
    assert exact_group.same_name is False
