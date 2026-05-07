from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SimilarComparisonQtMount:
    root_widget: Any
    left_image_label: Any | None = None
    right_image_label: Any | None = None
    info_label: Any | None = None
    action_buttons: dict[str, Any] = field(default_factory=dict)


def _text(value: object, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value).strip() or fallback


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _load_pixmap(QtGui: Any, path: str, max_width: int = 600, max_height: int = 500) -> Any:
    pixmap = QtGui.QPixmap(path)
    if pixmap.isNull():
        return None
    if pixmap.width() > max_width or pixmap.height() > max_height:
        pixmap = pixmap.scaled(
            max_width,
            max_height,
            QtGui.Qt.AspectRatioMode.KeepAspectRatio,
            QtGui.Qt.TransformationMode.SmoothTransformation,
        )
    return pixmap


def _add_label(parent: Any, QtWidgets: Any, text: str, **kwargs: object) -> Any:
    label = QtWidgets.QLabel(text)
    label.setWordWrap(True)
    for key, value in kwargs.items():
        label.setProperty(key, value)
    return label


def _add_button(parent: Any, QtWidgets: Any, text: str, enabled: bool = True) -> Any:
    button = QtWidgets.QPushButton(text)
    button.setEnabled(enabled)
    return button


def build_similar_comparison_page_widget(
    QtWidgets: Any,
    page: Mapping[str, Any],
    *,
    intent_dispatcher: Any | None = None,
) -> SimilarComparisonQtMount:
    QtCore = getattr(QtWidgets, "QtCore", None)
    QtGui = getattr(QtWidgets, "QtGui", None)
    if QtCore is None or QtGui is None:
        mount = SimilarComparisonQtMount(root_widget=QtWidgets.QWidget())
        return mount

    root = QtWidgets.QWidget()
    root_layout = QtWidgets.QVBoxLayout(root)
    root_layout.setContentsMargins(12, 12, 12, 12)

    title = _text(page.get("title"), "Similar Image Comparison")
    _add_label(root, QtWidgets, title, objectName="PageTitle")
    desc = _text(page.get("description"))
    if desc:
        _add_label(root, QtWidgets, desc, objectName="Muted")

    current_pair = _mapping(page.get("current_pair") or {})
    actions = list(page.get("actions") or [])

    mount = SimilarComparisonQtMount(root_widget=root)

    if not current_pair:
        empty = _mapping(page.get("empty_state") or {})
        _add_label(root, QtWidgets, _text(empty.get("title"), "No comparison pairs available."), objectName="Muted")
        return mount

    # Progress
    progress_text = (
        f"Group {page.get('current_group_index', 0) + 1} of {page.get('total_groups', 1)}  |  "
        f"Reviewed: {page.get('reviewed_count', 0)}  |  Remaining: {page.get('remaining_count', 0)}"
    )
    mount.info_label = _add_label(root, QtWidgets, progress_text, objectName="Progress")

    # Side-by-side image panels
    splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
    splitter.setChildrenCollapsible(False)

    # Left panel (keep)
    left_panel = QtWidgets.QWidget()
    left_layout = QtWidgets.QVBoxLayout(left_panel)
    left_layout.setContentsMargins(4, 4, 4, 4)

    keep = _mapping(current_pair.get("keep"))
    keep_path = keep.get("asset_path") or keep.get("path") or ""
    left_title = _add_label(left_panel, QtWidgets, "KEEP (Left)", objectName="Bold")
    mount.left_image_label = QtWidgets.QLabel()
    mount.left_image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    mount.left_image_label.setMinimumSize(300, 200)
    pixmap_left = _load_pixmap(QtGui, str(keep_path))
    if pixmap_left:
        mount.left_image_label.setPixmap(pixmap_left)
    else:
        mount.left_image_label.setText(f"[Image not available]\n{keep_path}")
    left_meta = _add_label(left_panel, QtWidgets, f"Path: {keep.get('path', '')}", objectName="Muted")
    left_meta.setWordWrap(True)

    left_layout.addWidget(left_title)
    left_layout.addWidget(mount.left_image_label, 1)
    left_layout.addWidget(left_meta)

    # Right panel (candidate)
    right_panel = QtWidgets.QWidget()
    right_layout = QtWidgets.QVBoxLayout(right_panel)
    right_layout.setContentsMargins(4, 4, 4, 4)

    candidate = _mapping(current_pair.get("candidate"))
    candidate_path = candidate.get("asset_path") or candidate.get("path") or ""
    candidate_distance = candidate.get("distance", 0)
    candidate_match = candidate.get("match_kind", "")
    candidate_priority = candidate.get("review_priority", "")

    right_title = _add_label(right_panel, QtWidgets, f"REVIEW (Right)  |  distance={candidate_distance}  |  {candidate_match}  |  priority={candidate_priority}", objectName="Bold")
    mount.right_image_label = QtWidgets.QLabel()
    mount.right_image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    mount.right_image_label.setMinimumSize(300, 200)
    pixmap_right = _load_pixmap(QtGui, str(candidate_path))
    if pixmap_right:
        mount.right_image_label.setPixmap(pixmap_right)
    else:
        mount.right_image_label.setText(f"[Image not available]\n{candidate_path}")
    right_meta = _add_label(right_panel, QtWidgets, f"Path: {candidate.get('path', '')}", objectName="Muted")
    right_meta.setWordWrap(True)

    right_layout.addWidget(right_title)
    right_layout.addWidget(mount.right_image_label, 1)
    right_layout.addWidget(right_meta)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setSizes([600, 600])
    root_layout.addWidget(splitter, 1)

    # Action buttons
    action_layout = QtWidgets.QHBoxLayout()
    action_map: dict[str, Any] = {}
    action_ids = ["keep-left", "keep-right", "keep-both", "skip"]
    for action in actions:
        action_id = _text(action.get("id"))
        if action_id not in action_ids:
            continue
        btn = _add_button(root, QtWidgets, _text(action.get("label"), action_id), enabled=bool(action.get("enabled")))
        if intent_dispatcher is not None:
            btn.clicked.connect(lambda checked=False, aid=action_id: intent_dispatcher({"intent_kind": aid}))
        action_layout.addWidget(btn)
        action_map[action_id] = btn
    root_layout.addLayout(action_layout)
    mount.action_buttons = action_map

    # Navigation buttons
    nav_layout = QtWidgets.QHBoxLayout()
    nav_ids = ["prev-candidate", "next-candidate"]
    for action in actions:
        action_id = _text(action.get("id"))
        if action_id not in nav_ids:
            continue
        btn = _add_button(root, QtWidgets, _text(action.get("label"), action_id), enabled=bool(action.get("enabled")))
        if intent_dispatcher is not None:
            btn.clicked.connect(lambda checked=False, aid=action_id: intent_dispatcher({"intent_kind": aid}))
        nav_layout.addWidget(btn)
        action_map[action_id] = btn
    root_layout.addLayout(nav_layout)

    mount.root_widget = root
    return mount
