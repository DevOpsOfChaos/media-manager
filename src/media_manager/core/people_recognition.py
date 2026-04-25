from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from media_manager.core.path_filters import path_is_included_by_patterns
from media_manager.media_formats import list_supported_similar_image_extensions, normalize_extensions
from media_manager.sorter import iter_media_files

SCHEMA_VERSION = 1
DEFAULT_TOLERANCE = 0.6
DEFAULT_BACKEND = "auto"
STRONG_BACKEND = "dlib"
BACKEND_CHOICES = ("auto", "dlib", "face-recognition", "opencv")
SUPPORTED_FACE_IMAGE_EXTENSIONS = frozenset(list_supported_similar_image_extensions())


@dataclass(slots=True, frozen=True)
class FaceBox:
    top: int
    right: int
    bottom: int
    left: int

    @classmethod
    def from_tuple(cls, value: tuple[int, int, int, int]) -> "FaceBox":
        top, right, bottom, left = value
        return cls(top=top, right=right, bottom=bottom, left=left)

    @classmethod
    def from_xywh(cls, *, x: int, y: int, width: int, height: int) -> "FaceBox":
        return cls(top=y, right=x + width, bottom=y + height, left=x)

    @classmethod
    def from_dlib_rect(cls, value: object) -> "FaceBox":
        return cls(
            top=int(value.top()),
            right=int(value.right()),
            bottom=int(value.bottom()),
            left=int(value.left()),
        )

    def to_dict(self) -> dict[str, int]:
        return {"top": self.top, "right": self.right, "bottom": self.bottom, "left": self.left}


@dataclass(slots=True, frozen=True)
class FaceMatch:
    person_id: str
    name: str | None
    distance: float

    def to_dict(self) -> dict[str, object]:
        return {"person_id": self.person_id, "name": self.name, "distance": round(self.distance, 6)}


@dataclass(slots=True, frozen=True)
class DetectedFace:
    path: Path
    face_index: int
    box: FaceBox
    encoding: tuple[float, ...] = ()
    match: FaceMatch | None = None
    cluster_id: str | None = None
    backend: str | None = None

    def to_dict(self, *, include_encoding: bool = False) -> dict[str, object]:
        payload: dict[str, object] = {
            "path": str(self.path),
            "face_index": self.face_index,
            "box": self.box.to_dict(),
            "backend": self.backend,
            "matched_person_id": self.match.person_id if self.match is not None else None,
            "matched_name": self.match.name if self.match is not None else None,
            "match_distance": round(self.match.distance, 6) if self.match is not None else None,
            "unknown_cluster_id": self.cluster_id,
        }
        if include_encoding:
            payload["encoding"] = [round(float(value), 10) for value in self.encoding]
        return payload


@dataclass(slots=True, frozen=True)
class PersonEmbedding:
    encoding: tuple[float, ...]
    source_path: str | None = None
    box: dict[str, int] | None = None
    created_at_utc: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {"encoding": [round(float(value), 10) for value in self.encoding]}
        if self.source_path:
            payload["source_path"] = self.source_path
        if self.box:
            payload["box"] = dict(self.box)
        if self.created_at_utc:
            payload["created_at_utc"] = self.created_at_utc
        return payload


@dataclass(slots=True)
class PersonRecord:
    person_id: str
    name: str | None = None
    aliases: list[str] = field(default_factory=list)
    notes: str = ""
    embeddings: list[PersonEmbedding] = field(default_factory=list)
    created_at_utc: str | None = None
    updated_at_utc: str | None = None

    def display_name(self) -> str | None:
        return self.name or (self.aliases[0] if self.aliases else None)

    def to_dict(self) -> dict[str, object]:
        return {
            "person_id": self.person_id,
            "name": self.name,
            "aliases": list(self.aliases),
            "notes": self.notes,
            "face_count": len(self.embeddings),
            "embeddings": [item.to_dict() for item in self.embeddings],
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }


@dataclass(slots=True)
class PeopleCatalog:
    persons: dict[str, PersonRecord] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION
    created_at_utc: str | None = None
    updated_at_utc: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
            "privacy_notice": "This file can contain face embeddings. Treat it as sensitive biometric metadata and keep it local/private.",
            "persons": [person.to_dict() for person in sorted(self.persons.values(), key=lambda item: item.person_id)],
        }


@dataclass(slots=True, frozen=True)
class PeopleScanConfig:
    source_dirs: list[Path]
    catalog_path: Path | None = None
    tolerance: float = DEFAULT_TOLERANCE
    backend: str = DEFAULT_BACKEND
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()
    media_extensions: frozenset[str] | None = None
    include_encodings_in_report: bool = False
    require_backend: bool = False


@dataclass(slots=True)
class BackendStatus:
    selected_backend: str | None
    available: bool
    dlib_available: bool
    face_recognition_available: bool
    opencv_available: bool
    detection_available: bool
    matching_available: bool
    unknown_grouping_available: bool
    next_action: str

    @property
    def strong_backend_available(self) -> bool:
        return self.dlib_available or self.face_recognition_available

    def to_dict(self) -> dict[str, object]:
        return {
            "selected_backend": self.selected_backend,
            "available": self.available,
            "dlib_available": self.dlib_available,
            "face_recognition_available": self.face_recognition_available,
            "opencv_available": self.opencv_available,
            "strong_backend_available": self.strong_backend_available,
            "capabilities": {
                "face_detection": self.detection_available,
                "named_person_matching": self.matching_available,
                "unknown_face_grouping": self.unknown_grouping_available,
            },
            "install_guidance": {
                "recommended_windows_extra": "people",
                "strong_backend_extra": "people-dlib",
                "opencv_only_extra": "people-opencv",
                "legacy_alias_extra": "people-face-recognition",
            },
            "next_action": self.next_action,
        }


@dataclass(slots=True)
class PeopleScanResult:
    status: str = "ok"
    backend: str | None = None
    backend_requested: str = DEFAULT_BACKEND
    backend_available: bool = False
    dlib_available: bool = False
    face_recognition_available: bool = False
    opencv_available: bool = False
    detection_available: bool = False
    matching_available: bool = False
    unknown_grouping_available: bool = False
    scanned_files: int = 0
    image_files: int = 0
    processed_files: int = 0
    skipped_filtered_files: int = 0
    skipped_unsupported_files: int = 0
    face_count: int = 0
    matched_faces: int = 0
    unknown_faces: int = 0
    unknown_cluster_count: int = 0
    detections: list[DetectedFace] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)
    catalog_person_count: int = 0
    next_action: str = "Review detected faces and add names to the local people catalog."

    def to_dict(self, *, include_encoding: bool = False) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": self.status,
            "backend": self.backend,
            "backend_requested": self.backend_requested,
            "backend_available": self.backend_available,
            "dlib_available": self.dlib_available,
            "face_recognition_available": self.face_recognition_available,
            "opencv_available": self.opencv_available,
            "strong_backend_available": self.dlib_available or self.face_recognition_available,
            "capabilities": {
                "face_detection": self.detection_available,
                "named_person_matching": self.matching_available,
                "unknown_face_grouping": self.unknown_grouping_available,
            },
            "summary": {
                "scanned_files": self.scanned_files,
                "image_files": self.image_files,
                "processed_files": self.processed_files,
                "skipped_filtered_files": self.skipped_filtered_files,
                "skipped_unsupported_files": self.skipped_unsupported_files,
                "face_count": self.face_count,
                "matched_faces": self.matched_faces,
                "unknown_faces": self.unknown_faces,
                "unknown_cluster_count": self.unknown_cluster_count,
                "catalog_person_count": self.catalog_person_count,
                "error_count": len(self.errors),
            },
            "detections": [item.to_dict(include_encoding=include_encoding) for item in self.detections],
            "errors": list(self.errors),
            "next_action": self.next_action,
            "privacy_notice": "People recognition is local and optional. Reports with encodings or catalogs can contain sensitive biometric metadata.",
        }


def _now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_backend():
    """Return the legacy optional face_recognition package backend.

    Kept for compatibility with earlier tests and callers. The preferred strong
    backend is now the direct dlib backend because the face_recognition package
    often forces a dlib source build on Windows.
    """
    try:  # pragma: no cover - optional runtime dependency
        import face_recognition  # type: ignore
    except Exception:
        return None
    return face_recognition


def _load_dlib_backend():
    """Return a direct dlib backend using packaged face-recognition model files.

    On Windows this is intended to be installed through the dlib-bin wheel, not
    by compiling dlib from source. It provides detection plus 128-dimensional
    embeddings for local named-person matching.
    """
    try:  # pragma: no cover - optional runtime dependency
        import dlib  # type: ignore
        import face_recognition_models  # type: ignore
        import numpy as np  # type: ignore
        from PIL import Image  # type: ignore
    except Exception:
        return None

    try:  # pragma: no cover - optional runtime/model dependent
        pose_model_path = face_recognition_models.pose_predictor_five_point_model_location()
    except AttributeError:  # pragma: no cover - older model package fallback
        pose_model_path = face_recognition_models.pose_predictor_model_location()

    try:  # pragma: no cover - optional runtime/model dependent
        return {
            "dlib": dlib,
            "np": np,
            "Image": Image,
            "detector": dlib.get_frontal_face_detector(),
            "shape_predictor": dlib.shape_predictor(pose_model_path),
            "face_encoder": dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location()),
            "pose_model_path": str(pose_model_path),
            "face_model_path": str(face_recognition_models.face_recognition_model_location()),
        }
    except Exception:
        return None


def _load_opencv_backend():
    try:  # pragma: no cover - optional runtime dependency
        import cv2  # type: ignore
    except Exception:
        return None
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    classifier = cv2.CascadeClassifier(str(cascade_path))
    if classifier.empty():
        return None
    return {"cv2": cv2, "classifier": classifier, "cascade_path": str(cascade_path)}


def _validate_backend_name(backend: str) -> str:
    normalized = str(backend or DEFAULT_BACKEND).strip().lower().replace("_", "-")
    if normalized in {"dlib-bin", "dlibbin"}:
        normalized = "dlib"
    if normalized == "face-recognition-models":
        normalized = "dlib"
    if normalized == "face-recognition" or normalized == "face-recognition-package":
        normalized = "face-recognition"
    if normalized not in BACKEND_CHOICES:
        raise ValueError(f"Unsupported people recognition backend: {backend}")
    return normalized


def inspect_people_backend(preferred_backend: str = DEFAULT_BACKEND) -> BackendStatus:
    preferred = _validate_backend_name(preferred_backend)
    dlib_backend = _load_dlib_backend()
    face_backend = _load_backend()
    opencv_backend = _load_opencv_backend()
    dlib_available = dlib_backend is not None
    face_available = face_backend is not None
    opencv_available = opencv_backend is not None

    selected: str | None = None
    matching_available = False
    grouping_available = False
    if preferred in {"auto", "dlib", "face-recognition"} and dlib_available:
        selected = "dlib"
        matching_available = True
        grouping_available = True
    elif preferred in {"auto", "face-recognition"} and face_available:
        selected = "face-recognition"
        matching_available = True
        grouping_available = True
    elif preferred in {"auto", "opencv"} and opencv_available:
        selected = "opencv"
    available = selected is not None

    if selected == "dlib":
        next_action = "Best local backend is available: dlib wheel backend with face embeddings and named-person matching."
    elif selected == "face-recognition":
        next_action = "Legacy face_recognition backend is available with face embeddings and named-person matching."
    elif selected == "opencv":
        next_action = (
            "OpenCV face detection is available. Named-person matching is disabled; "
            "install the people-dlib extra for the stronger local recognition backend."
        )
    elif preferred in {"dlib", "face-recognition"}:
        next_action = (
            "The strong people backend is not installed or could not be loaded. "
            "On Windows, run: python -m pip install -e .[people-dlib]"
        )
    elif preferred == "opencv":
        next_action = "The OpenCV backend is not installed or could not be loaded. Run: python -m pip install -e .[people-opencv]"
    else:
        next_action = "Install a people backend. Recommended on Windows: python -m pip install -e .[people]"

    return BackendStatus(
        selected_backend=selected,
        available=available,
        dlib_available=dlib_available,
        face_recognition_available=face_available,
        opencv_available=opencv_available,
        detection_available=available,
        matching_available=matching_available,
        unknown_grouping_available=grouping_available,
        next_action=next_action,
    )


def backend_available(preferred_backend: str = DEFAULT_BACKEND) -> bool:
    return inspect_people_backend(preferred_backend).available


def _source_root_for_path(path: Path, source_dirs: list[Path]) -> Path | None:
    for source_dir in sorted(source_dirs, key=lambda item: len(str(item)), reverse=True):
        try:
            path.relative_to(source_dir)
        except ValueError:
            continue
        return source_dir
    return None


def _coerce_float_tuple(values: Iterable[object]) -> tuple[float, ...]:
    return tuple(float(value) for value in values)


def _load_embedding(value: Mapping[str, object]) -> PersonEmbedding | None:
    raw_encoding = value.get("encoding")
    if not isinstance(raw_encoding, list):
        return None
    try:
        encoding = _coerce_float_tuple(raw_encoding)
    except (TypeError, ValueError):
        return None
    source_path = value.get("source_path") if isinstance(value.get("source_path"), str) else None
    box = value.get("box") if isinstance(value.get("box"), dict) else None
    normalized_box = {str(key): int(raw) for key, raw in box.items()} if box else None
    created_at = value.get("created_at_utc") if isinstance(value.get("created_at_utc"), str) else None
    return PersonEmbedding(encoding=encoding, source_path=source_path, box=normalized_box, created_at_utc=created_at)


def load_people_catalog(path: str | Path | None) -> PeopleCatalog:
    if path is None:
        return PeopleCatalog(created_at_utc=_now_utc(), updated_at_utc=_now_utc())
    catalog_path = Path(path)
    if not catalog_path.exists():
        return PeopleCatalog(created_at_utc=_now_utc(), updated_at_utc=_now_utc())
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected people catalog JSON object in {catalog_path}")
    catalog = PeopleCatalog(
        schema_version=int(payload.get("schema_version", SCHEMA_VERSION)),
        created_at_utc=payload.get("created_at_utc") if isinstance(payload.get("created_at_utc"), str) else None,
        updated_at_utc=payload.get("updated_at_utc") if isinstance(payload.get("updated_at_utc"), str) else None,
    )
    persons = payload.get("persons", [])
    if not isinstance(persons, list):
        raise ValueError(f"Expected persons list in {catalog_path}")
    for raw_person in persons:
        if not isinstance(raw_person, dict):
            continue
        person_id = raw_person.get("person_id")
        if not isinstance(person_id, str) or not person_id.strip():
            continue
        raw_aliases = raw_person.get("aliases", [])
        aliases = [str(item) for item in raw_aliases] if isinstance(raw_aliases, list) else []
        record = PersonRecord(
            person_id=person_id,
            name=raw_person.get("name") if isinstance(raw_person.get("name"), str) else None,
            aliases=aliases,
            notes=raw_person.get("notes") if isinstance(raw_person.get("notes"), str) else "",
            created_at_utc=raw_person.get("created_at_utc") if isinstance(raw_person.get("created_at_utc"), str) else None,
            updated_at_utc=raw_person.get("updated_at_utc") if isinstance(raw_person.get("updated_at_utc"), str) else None,
        )
        raw_embeddings = raw_person.get("embeddings", [])
        if isinstance(raw_embeddings, list):
            for raw_embedding in raw_embeddings:
                if isinstance(raw_embedding, dict):
                    embedding = _load_embedding(raw_embedding)
                    if embedding is not None:
                        record.embeddings.append(embedding)
        catalog.persons[record.person_id] = record
    return catalog


def write_people_catalog(path: str | Path, catalog: PeopleCatalog) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    catalog.updated_at_utc = _now_utc()
    if catalog.created_at_utc is None:
        catalog.created_at_utc = catalog.updated_at_utc
    output_path.write_text(json.dumps(catalog.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def _person_id_from_name(name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    return "person-" + ("-".join(part for part in slug.split("-") if part) or "unnamed")


def _unique_person_id(catalog: PeopleCatalog, preferred: str) -> str:
    candidate = preferred
    counter = 2
    while candidate in catalog.persons:
        candidate = f"{preferred}-{counter}"
        counter += 1
    return candidate


def add_person_to_catalog(
    catalog: PeopleCatalog,
    *,
    name: str,
    person_id: str | None = None,
    aliases: Iterable[str] = (),
    notes: str = "",
) -> PersonRecord:
    resolved_id = _unique_person_id(catalog, person_id or _person_id_from_name(name))
    now = _now_utc()
    record = PersonRecord(
        person_id=resolved_id,
        name=name,
        aliases=[str(item) for item in aliases if str(item)],
        notes=notes,
        created_at_utc=now,
        updated_at_utc=now,
    )
    catalog.persons[resolved_id] = record
    return record


def rename_person_in_catalog(catalog: PeopleCatalog, *, person_id: str, name: str) -> PersonRecord:
    if person_id not in catalog.persons:
        raise KeyError(f"Unknown person_id: {person_id}")
    record = catalog.persons[person_id]
    record.name = name
    record.updated_at_utc = _now_utc()
    return record


def add_embedding_to_person(
    catalog: PeopleCatalog,
    *,
    person_id: str,
    encoding: Iterable[float],
    source_path: str | None = None,
    box: Mapping[str, int] | None = None,
) -> PersonEmbedding:
    if person_id not in catalog.persons:
        raise KeyError(f"Unknown person_id: {person_id}")
    embedding = PersonEmbedding(
        encoding=tuple(float(value) for value in encoding),
        source_path=source_path,
        box={str(key): int(value) for key, value in box.items()} if box else None,
        created_at_utc=_now_utc(),
    )
    record = catalog.persons[person_id]
    record.embeddings.append(embedding)
    record.updated_at_utc = _now_utc()
    return embedding


def _euclidean_distance(first: Iterable[float], second: Iterable[float]) -> float:
    return math.sqrt(sum((float(left) - float(right)) ** 2 for left, right in zip(first, second, strict=True)))


def _best_match(encoding: tuple[float, ...], catalog: PeopleCatalog, *, tolerance: float) -> FaceMatch | None:
    if not encoding:
        return None
    best: FaceMatch | None = None
    for person in catalog.persons.values():
        for known in person.embeddings:
            if len(known.encoding) != len(encoding):
                continue
            distance = _euclidean_distance(encoding, known.encoding)
            if distance > tolerance:
                continue
            if best is None or distance < best.distance:
                best = FaceMatch(person_id=person.person_id, name=person.display_name(), distance=distance)
    return best


def _cluster_unknown_faces(detections: list[DetectedFace], *, tolerance: float) -> list[DetectedFace]:
    cluster_centroids: list[tuple[float, ...]] = []
    cluster_ids: list[str] = []
    clustered: list[DetectedFace] = []
    for detection in detections:
        if detection.match is not None:
            clustered.append(detection)
            continue
        assigned_id: str | None = None
        if detection.encoding:
            for index, centroid in enumerate(cluster_centroids):
                if len(centroid) == len(detection.encoding) and _euclidean_distance(detection.encoding, centroid) <= tolerance:
                    assigned_id = cluster_ids[index]
                    break
        if assigned_id is None:
            digest = hashlib.sha1((str(detection.path) + ":" + str(detection.face_index)).encode("utf-8")).hexdigest()[:10]
            assigned_id = f"unknown-{len(cluster_ids) + 1}-{digest}"
            cluster_ids.append(assigned_id)
            if detection.encoding:
                cluster_centroids.append(detection.encoding)
        clustered.append(
            DetectedFace(
                path=detection.path,
                face_index=detection.face_index,
                box=detection.box,
                encoding=detection.encoding,
                match=detection.match,
                cluster_id=assigned_id,
                backend=detection.backend,
            )
        )
    return clustered


def _detect_faces_with_face_recognition(path: Path, backend) -> list[tuple[FaceBox, tuple[float, ...]]]:
    image = backend.load_image_file(str(path))
    locations = backend.face_locations(image)
    encodings = backend.face_encodings(image, known_face_locations=locations)
    records: list[tuple[FaceBox, tuple[float, ...]]] = []
    for location, encoding in zip(locations, encodings, strict=False):
        records.append((FaceBox.from_tuple(tuple(int(item) for item in location)), tuple(float(item) for item in encoding)))
    return records


def _load_image_array_for_dlib(path: Path, backend):
    with backend["Image"].open(path) as handle:
        return backend["np"].array(handle.convert("RGB"))


def _detect_faces_with_dlib(path: Path, backend) -> list[tuple[FaceBox, tuple[float, ...]]]:
    image = _load_image_array_for_dlib(path, backend)
    rectangles = backend["detector"](image, 1)
    records: list[tuple[FaceBox, tuple[float, ...]]] = []
    for rectangle in rectangles:
        shape = backend["shape_predictor"](image, rectangle)
        descriptor = backend["face_encoder"].compute_face_descriptor(image, shape)
        records.append((FaceBox.from_dlib_rect(rectangle), tuple(float(value) for value in descriptor)))
    return records


def _detect_faces_with_opencv(path: Path, backend) -> list[tuple[FaceBox, tuple[float, ...]]]:
    cv2 = backend["cv2"]
    classifier = backend["classifier"]
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError("OpenCV could not read image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24))
    records: list[tuple[FaceBox, tuple[float, ...]]] = []
    for x, y, width, height in faces:
        records.append((FaceBox.from_xywh(x=int(x), y=int(y), width=int(width), height=int(height)), ()))
    return records


def _selected_backend(preferred_backend: str):
    preferred = _validate_backend_name(preferred_backend)
    if preferred in {"auto", "dlib", "face-recognition"}:
        backend = _load_dlib_backend()
        if backend is not None:
            return "dlib", backend
        if preferred == "dlib":
            return None, None
    if preferred in {"auto", "face-recognition"}:
        backend = _load_backend()
        if backend is not None:
            return "face-recognition", backend
        if preferred == "face-recognition":
            return None, None
    if preferred in {"auto", "opencv"}:
        backend = _load_opencv_backend()
        if backend is not None:
            return "opencv", backend
    return None, None


def scan_people(config: PeopleScanConfig) -> PeopleScanResult:
    if config.tolerance <= 0:
        raise ValueError("tolerance must be greater than zero")

    requested_backend = _validate_backend_name(config.backend)
    result = PeopleScanResult(backend_requested=requested_backend)
    catalog = load_people_catalog(config.catalog_path)
    result.catalog_person_count = len(catalog.persons)

    scan_extensions = SUPPORTED_FACE_IMAGE_EXTENSIONS
    if config.media_extensions is not None:
        scan_extensions = normalize_extensions(config.media_extensions) & set(SUPPORTED_FACE_IMAGE_EXTENSIONS)
    media_files = iter_media_files(config.source_dirs, media_extensions=scan_extensions)
    result.scanned_files = len(media_files)

    backend_status = inspect_people_backend(requested_backend)
    result.dlib_available = backend_status.dlib_available
    result.face_recognition_available = backend_status.face_recognition_available
    result.opencv_available = backend_status.opencv_available
    result.backend_available = backend_status.available
    result.detection_available = backend_status.detection_available
    result.matching_available = backend_status.matching_available
    result.unknown_grouping_available = backend_status.unknown_grouping_available
    result.backend = backend_status.selected_backend

    selected_name, backend = _selected_backend(requested_backend)
    if backend is None or selected_name is None:
        result.status = "backend_missing"
        result.next_action = backend_status.next_action
        if config.require_backend:
            result.errors.append({"path": "", "error": f"people backend is not installed: {requested_backend}"})
        return result

    image_files: list[Path] = []
    for path in media_files:
        if path.suffix.lower() not in SUPPORTED_FACE_IMAGE_EXTENSIONS:
            result.skipped_unsupported_files += 1
            continue
        if path_is_included_by_patterns(
            path,
            include_patterns=config.include_patterns,
            exclude_patterns=config.exclude_patterns,
            source_root=_source_root_for_path(path, config.source_dirs),
        ):
            image_files.append(path)
        else:
            result.skipped_filtered_files += 1

    result.image_files = len(image_files)
    detections: list[DetectedFace] = []
    for path in image_files:
        try:
            if selected_name == "dlib":
                faces = _detect_faces_with_dlib(path, backend)
            elif selected_name == "face-recognition":
                faces = _detect_faces_with_face_recognition(path, backend)
            else:
                faces = _detect_faces_with_opencv(path, backend)
            result.processed_files += 1
        except Exception as exc:  # pragma: no cover - backend/runtime dependent
            result.errors.append({"path": str(path), "error": str(exc)})
            continue
        for face_index, (box, encoding) in enumerate(faces):
            match = _best_match(encoding, catalog, tolerance=config.tolerance)
            detections.append(
                DetectedFace(
                    path=path,
                    face_index=face_index,
                    box=box,
                    encoding=encoding,
                    match=match,
                    backend=selected_name,
                )
            )

    result.detections = _cluster_unknown_faces(detections, tolerance=config.tolerance)
    result.face_count = len(result.detections)
    result.matched_faces = sum(1 for item in result.detections if item.match is not None)
    result.unknown_faces = result.face_count - result.matched_faces
    result.unknown_cluster_count = len({item.cluster_id for item in result.detections if item.cluster_id})
    if result.errors:
        result.status = "completed_with_errors"
    if selected_name == "opencv":
        result.next_action = (
            "Review detected faces. OpenCV detects faces locally, but named-person matching requires "
            "the optional people-dlib backend."
        )
    return result


def build_people_review_payload(scan_payload: Mapping[str, object]) -> dict[str, object]:
    detections = scan_payload.get("detections", [])
    if not isinstance(detections, list):
        detections = []
    candidates = []
    for item in detections:
        if not isinstance(item, Mapping):
            continue
        if item.get("matched_person_id"):
            continue
        candidates.append(
            {
                "path": item.get("path"),
                "face_index": item.get("face_index"),
                "box": item.get("box"),
                "backend": item.get("backend"),
                "unknown_cluster_id": item.get("unknown_cluster_id"),
                "reason": "unknown_face",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "people",
        "candidate_count": len(candidates),
        "reason_summary": {"unknown_face": len(candidates)} if candidates else {},
        "candidates": candidates,
        "privacy_notice": "Review payloads can reveal who appears in which local files. Keep them private.",
    }


__all__ = [
    "BACKEND_CHOICES",
    "DEFAULT_BACKEND",
    "DEFAULT_TOLERANCE",
    "PeopleCatalog",
    "PeopleScanConfig",
    "PeopleScanResult",
    "SCHEMA_VERSION",
    "STRONG_BACKEND",
    "add_embedding_to_person",
    "add_person_to_catalog",
    "backend_available",
    "build_people_review_payload",
    "inspect_people_backend",
    "load_people_catalog",
    "rename_person_in_catalog",
    "scan_people",
    "write_people_catalog",
]
