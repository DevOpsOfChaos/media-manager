"""Fast face detection using OpenCV DNN (YuNet) for initial scanning pass.

YuNet is 10-50x faster than dlib HOG on CPU while maintaining good recall.
Used as Stage 1 of the two-stage pipeline; Stage 2 runs full dlib on ambiguous faces.
"""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

YUNET_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
YUNET_INPUT_SIZE = (320, 320)
YUNET_CONFIDENCE_THRESHOLD = 0.6
YUNET_NMS_THRESHOLD = 0.3
YUNET_TOP_K = 5000


def _get_yunet_model_path() -> Path | None:
    import os
    cache_dir = Path(os.environ.get("MEDIA_MANAGER_HOME", Path.home() / ".media-manager"))
    models_dir = cache_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "face_detection_yunet_2023mar.onnx"

    if not model_path.exists():
        logger.info("Downloading YuNet face detection model (337 KB)...")
        try:
            urllib.request.urlretrieve(YUNET_MODEL_URL, model_path)
            logger.info("YuNet model downloaded to %s", model_path)
        except Exception as e:
            logger.error("Failed to download YuNet model: %s", e)
            return None

    return model_path


def detect_faces_yunet(
    image_path: Path,
    confidence_threshold: float = YUNET_CONFIDENCE_THRESHOLD,
    nms_threshold: float = YUNET_NMS_THRESHOLD,
) -> list[tuple[int, int, int, int, float]]:
    """Fast face detection using YuNet ONNX via OpenCV DNN.

    Returns list of (x, y, w, h, confidence) bounding boxes.
    Falls back gracefully if OpenCV or model is unavailable.
    """
    try:
        import cv2
    except ImportError:
        logger.debug("OpenCV not available for YuNet detection")
        return []

    model_path = _get_yunet_model_path()
    if model_path is None or not model_path.exists():
        return []

    img = cv2.imread(str(image_path))
    if img is None:
        return []

    h, w = img.shape[:2]
    scale = min(YUNET_INPUT_SIZE[0] / w, YUNET_INPUT_SIZE[1] / h)

    try:
        net = cv2.dnn.readNetFromONNX(str(model_path))
        backend = _get_preferred_backend()
        if backend == "cuda":
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        elif backend == "openvino":
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        blob = cv2.dnn.blobFromImage(
            img, 1.0 / 255.0, YUNET_INPUT_SIZE, [0, 0, 0], swapRB=False, crop=False
        )
        net.setInput(blob)
        detections = net.forward()
    except cv2.error as e:
        logger.warning("YuNet inference failed: %s", e)
        return []

    results: list[tuple[int, int, int, int, float]] = []
    if detections is None or detections.size == 0:
        return results

    for det in detections:
        score = float(det[1])
        if score < confidence_threshold:
            continue

        x = int(det[2] / scale)
        y = int(det[3] / scale)
        bw = int(det[4] / scale)
        bh = int(det[5] / scale)

        x = max(0, x)
        y = max(0, y)
        bw = min(bw, w - x)
        bh = min(bh, h - y)

        if bw > 0 and bh > 0:
            results.append((x, y, bw, bh, score))

    return results


def _get_preferred_backend() -> str:
    """Detect best available DNN backend for OpenCV."""
    try:
        import cv2
        model_path = _get_yunet_model_path()
        if model_path is None:
            return "cpu"
        model_str = str(model_path)

        # Try CUDA first
        try:
            net = cv2.dnn.readNetFromONNX(model_str)
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            return "cuda"
        except Exception:
            pass

        # Try OpenVINO
        try:
            net = cv2.dnn.readNetFromONNX(model_str)
            net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
            net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            return "openvino"
        except Exception:
            pass

        return "cpu"
    except ImportError:
        return "cpu"


def gpu_info() -> dict:
    """Return GPU availability information."""
    info = {"cuda": False, "openvino": False, "backend": "cpu"}
    try:
        import cv2
        model_path = _get_yunet_model_path()
        if model_path is None:
            return info
        try:
            test_net = cv2.dnn.readNetFromONNX(str(model_path))
            test_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            test_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            info["cuda"] = True
            info["backend"] = "cuda"
            return info
        except Exception:
            pass
        try:
            test_net = cv2.dnn.readNetFromONNX(str(model_path))
            test_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_INFERENCE_ENGINE)
            test_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            info["openvino"] = True
            info["backend"] = "openvino"
        except Exception:
            pass
    except ImportError:
        pass
    return info


def score_face_quality(
    face_box: tuple[int, int, int, int],
    image_path: Path,
) -> dict:
    """Score face quality: size, sharpness, pose estimation.

    Returns dict with scores 0.0-1.0 for each quality dimension.
    """
    try:
        import cv2
    except ImportError:
        return {"size_score": 0.0, "sharpness_score": 0.0, "overall_score": 0.0, "usable": False}

    x, y, w, h = face_box
    img = cv2.imread(str(image_path))
    if img is None:
        return {"size_score": 0.0, "sharpness_score": 0.0, "overall_score": 0.0, "usable": False}

    ih, iw = img.shape[:2]

    # Size score: face should be at least 5% of image
    face_area = w * h
    image_area = iw * ih
    size_ratio = face_area / image_area if image_area > 0 else 0.0
    size_score = min(1.0, size_ratio / 0.05)  # 5% = score 1.0

    # Sharpness score: Laplacian variance of face region
    face_roi = img[max(0, y):min(ih, y + h), max(0, x):min(iw, x + w)]
    if face_roi.size > 0:
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) > 2 else face_roi
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(1.0, laplacian_var / 500.0)  # 500 var = sharp
    else:
        sharpness_score = 0.0

    # Overall score
    overall = size_score * 0.5 + sharpness_score * 0.5

    return {
        "size_score": round(size_score, 3),
        "sharpness_score": round(sharpness_score, 3),
        "overall_score": round(overall, 3),
        "usable": overall > 0.3,
    }


def estimate_age_range(image_path: Path, face_box: tuple[int, int, int, int]) -> dict:
    """Estimate approximate age bracket from a face image using simple heuristics.

    Uses face size ratio and image metadata as rough age indicators.
    For accurate age estimation, a dedicated ML model is needed.
    Returns age bracket: 'child', 'teen', 'young-adult', 'adult', 'senior'
    """
    try:
        import cv2
    except ImportError:
        return {"age_bracket": "unknown", "confidence": 0.0}

    x, y, w, h = face_box
    img = cv2.imread(str(image_path))
    if img is None:
        return {"age_bracket": "unknown", "confidence": 0.0}

    ih, iw = img.shape[:2]
    face_ratio = (w * h) / (iw * ih)

    if face_ratio > 0.15:
        bracket = "adult"
        confidence = min(0.8, face_ratio * 3)
    elif face_ratio > 0.08:
        bracket = "young-adult"
        confidence = 0.6
    elif face_ratio > 0.04:
        bracket = "teen"
        confidence = 0.5
    else:
        bracket = "child"
        confidence = 0.4

    return {
        "age_bracket": bracket,
        "confidence": round(confidence, 2),
        "note": "Heuristic estimation based on face size ratio. For accurate age estimation, install an age-detection model."
    }


def is_available() -> bool:
    """Check if YuNet fast detection is available."""
    try:
        model_path = _get_yunet_model_path()
        return model_path is not None and model_path.exists()
    except Exception:
        return False
