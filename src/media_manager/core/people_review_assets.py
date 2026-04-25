from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

ASSET_SCHEMA_VERSION = 1
ASSET_KIND = "people_review_assets"
DEFAULT_THUMBNAIL_SIZE = 256
DEFAULT_CROP_PADDING_RATIO = 0.25


def _as_text(value: object) -> str:
    return value if isinstance(value, str) else ""


def _as_int(value: object, *, default: int = 0) -> int:
    return value if isinstance(value, int) else default


def _as_bool(value: object, *, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _as_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def face_id_for_detection(path: object, face_index: object) -> str:
    token = f"{_as_text(path)}::{int(face_index) if isinstance(face_index, int) else face_index}"
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()[:16]
    return f"face-{digest}"


def _detections_by_face_id(report_payload: Mapping[str, object]) -> dict[str, Mapping[str, object]]:
    result: dict[str, Mapping[str, object]] = {}
    for raw_item in _as_list(report_payload.get("detections")):
        if not isinstance(raw_item, Mapping):
            continue
        face_id = face_id_for_detection(raw_item.get("path"), raw_item.get("face_index"))
        result[face_id] = raw_item
    return result


def _workflow_context_by_face_id(workflow_payload: Mapping[str, object] | None) -> dict[str, dict[str, object]]:
    if workflow_payload is None:
        return {}
    contexts: dict[str, dict[str, object]] = {}
    for raw_group in _as_list(workflow_payload.get("groups")):
        if not isinstance(raw_group, Mapping):
            continue
        group_id = _as_text(raw_group.get("review_group_id"))
        for raw_face in _as_list(raw_group.get("faces")):
            if not isinstance(raw_face, Mapping):
                continue
            face_id = _as_text(raw_face.get("face_id")) or face_id_for_detection(raw_face.get("path"), raw_face.get("face_index"))
            contexts[face_id] = {
                "review_group_id": group_id,
                "group_type": raw_group.get("group_type"),
                "include": _as_bool(raw_face.get("include"), default=True),
                "apply_group": _as_bool(raw_group.get("apply_group"), default=False),
                "selected_person_id": raw_group.get("selected_person_id", ""),
                "selected_name": raw_group.get("selected_name", ""),
                "suggested_person_id": raw_group.get("suggested_person_id", ""),
                "suggested_name": raw_group.get("suggested_name", ""),
            }
    return contexts


def _normalize_box(box: Mapping[str, object]) -> tuple[int, int, int, int] | None:
    top = _as_int(box.get("top"), default=0)
    right = _as_int(box.get("right"), default=0)
    bottom = _as_int(box.get("bottom"), default=0)
    left = _as_int(box.get("left"), default=0)
    if right <= left or bottom <= top:
        return None
    return left, top, right, bottom


def _padded_crop_box(
    box: tuple[int, int, int, int],
    *,
    image_width: int,
    image_height: int,
    padding_ratio: float,
) -> tuple[int, int, int, int] | None:
    left, top, right, bottom = box
    width = max(0, right - left)
    height = max(0, bottom - top)
    if width <= 0 or height <= 0:
        return None
    padding_x = int(round(width * max(0.0, padding_ratio)))
    padding_y = int(round(height * max(0.0, padding_ratio)))
    padded = (
        max(0, left - padding_x),
        max(0, top - padding_y),
        min(image_width, right + padding_x),
        min(image_height, bottom + padding_y),
    )
    if padded[2] <= padded[0] or padded[3] <= padded[1]:
        return None
    return padded


def _relative_asset_path(asset_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(asset_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _write_face_crop(
    *,
    detection: Mapping[str, object],
    face_id: str,
    asset_dir: Path,
    padding_ratio: float,
    thumbnail_size: int,
    quality: int,
    overwrite: bool,
) -> dict[str, object]:
    source_text = _as_text(detection.get("path"))
    source_path = Path(source_text)
    output_dir = asset_dir / "faces"
    output_path = output_dir / f"{face_id}.jpg"
    base_payload: dict[str, object] = {
        "face_id": face_id,
        "path": source_text,
        "face_index": detection.get("face_index"),
        "box": detection.get("box"),
        "backend": detection.get("backend"),
        "matched_person_id": detection.get("matched_person_id"),
        "matched_name": detection.get("matched_name"),
        "unknown_cluster_id": detection.get("unknown_cluster_id"),
        "asset_path": output_path.as_posix(),
        "asset_relative_path": _relative_asset_path(asset_dir, output_path),
        "image_uri": {"type": "local_path", "value": output_path.as_posix()},
    }

    if output_path.exists() and not overwrite:
        base_payload.update({"status": "exists", "error": None})
        return base_payload

    raw_box = _as_mapping(detection.get("box"))
    normalized_box = _normalize_box(raw_box)
    if normalized_box is None:
        base_payload.update({"status": "error", "error": "invalid_face_box"})
        return base_payload

    if not source_path.exists():
        base_payload.update({"status": "error", "error": "source_image_missing"})
        return base_payload

    try:
        with Image.open(source_path) as image:
            rgb = image.convert("RGB")
            crop_box = _padded_crop_box(
                normalized_box,
                image_width=rgb.width,
                image_height=rgb.height,
                padding_ratio=padding_ratio,
            )
            if crop_box is None:
                base_payload.update({"status": "error", "error": "invalid_padded_crop_box"})
                return base_payload
            crop = rgb.crop(crop_box)
            crop.thumbnail((thumbnail_size, thumbnail_size))
            output_dir.mkdir(parents=True, exist_ok=True)
            crop.save(output_path, format="JPEG", quality=max(1, min(100, int(quality))))
            base_payload.update(
                {
                    "status": "ok",
                    "error": None,
                    "source_image_size": {"width": rgb.width, "height": rgb.height},
                    "crop_box": {"left": crop_box[0], "top": crop_box[1], "right": crop_box[2], "bottom": crop_box[3]},
                    "asset_size": {"width": crop.width, "height": crop.height},
                }
            )
            return base_payload
    except Exception as exc:  # pragma: no cover - depends on image decoder/runtime
        base_payload.update({"status": "error", "error": str(exc)})
        return base_payload


def build_people_review_assets(
    *,
    report_payload: Mapping[str, object],
    asset_dir: str | Path,
    workflow_payload: Mapping[str, object] | None = None,
    crop_padding_ratio: float = DEFAULT_CROP_PADDING_RATIO,
    thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE,
    quality: int = 90,
    overwrite: bool = True,
) -> dict[str, object]:
    """Write local face crop assets for a GUI people review page.

    The output manifest intentionally references local paths only. It is meant to
    stay next to the run artifacts and never uploads face data anywhere.
    """

    resolved_asset_dir = Path(asset_dir)
    detections = _detections_by_face_id(report_payload)
    contexts = _workflow_context_by_face_id(workflow_payload)
    selected_face_ids = set(contexts) if contexts else set(detections)
    assets: list[dict[str, object]] = []

    for face_id in sorted(selected_face_ids):
        detection = detections.get(face_id)
        if detection is None:
            assets.append(
                {
                    "face_id": face_id,
                    "status": "error",
                    "error": "face_not_found_in_report",
                    **contexts.get(face_id, {}),
                }
            )
            continue
        asset = _write_face_crop(
            detection=detection,
            face_id=face_id,
            asset_dir=resolved_asset_dir,
            padding_ratio=crop_padding_ratio,
            thumbnail_size=thumbnail_size,
            quality=quality,
            overwrite=overwrite,
        )
        asset.update(contexts.get(face_id, {}))
        assets.append(asset)

    generated_count = sum(1 for item in assets if item.get("status") == "ok")
    existing_count = sum(1 for item in assets if item.get("status") == "exists")
    error_count = sum(1 for item in assets if item.get("status") == "error")
    return {
        "schema_version": ASSET_SCHEMA_VERSION,
        "kind": ASSET_KIND,
        "asset_dir": resolved_asset_dir.as_posix(),
        "crop_padding_ratio": crop_padding_ratio,
        "thumbnail_size": thumbnail_size,
        "quality": quality,
        "summary": {
            "asset_count": len(assets),
            "generated_count": generated_count,
            "existing_count": existing_count,
            "error_count": error_count,
        },
        "assets": assets,
        "privacy_notice": "Face crop assets reveal who appears in local files. Keep this directory local/private.",
    }


def write_people_review_asset_manifest(path: str | Path, payload: Mapping[str, object]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dict(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


__all__ = [
    "ASSET_KIND",
    "ASSET_SCHEMA_VERSION",
    "DEFAULT_CROP_PADDING_RATIO",
    "DEFAULT_THUMBNAIL_SIZE",
    "build_people_review_assets",
    "face_id_for_detection",
    "write_people_review_asset_manifest",
]
