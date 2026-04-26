from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .gui_qt_change_summary import build_change_summary
from .gui_qt_pending_changes import normalize_pending_changes, summarize_pending_changes
from .gui_qt_review_apply_preview import build_qt_review_apply_preview
from .gui_qt_save_state import build_workspace_save_state
from .gui_qt_undo_redo_stack import build_undo_redo_stack
from .gui_qt_workspace_flow import build_workspace_flow
from .gui_qt_workspace_guard import build_workspace_guard

REVIEW_WORKBENCH_SCHEMA_VERSION = "1.0"


def build_qt_review_workbench(
    *,
    page_model: Mapping[str, Any],
    pending_changes: Iterable[Mapping[str, Any]] = (),
    workspace_path: str | None = None,
    undo: list[Mapping[str, Any]] | None = None,
    redo: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    changes = normalize_pending_changes(pending_changes)
    pending_summary = summarize_pending_changes(changes)
    save_state = build_workspace_save_state(workspace_path=workspace_path, pending_change_count=pending_summary["pending_count"])
    stack = build_undo_redo_stack(undo=undo or changes, redo=redo or [])
    state: dict[str, Any] = {
        "schema_version": REVIEW_WORKBENCH_SCHEMA_VERSION,
        "kind": "qt_review_workbench",
        "page": dict(page_model),
        "pending_changes": changes,
        "pending_summary": pending_summary,
        "change_summary": build_change_summary(changes),
        "save_state": save_state,
        "undo_redo": stack,
        "executes_immediately": False,
    }
    state["apply_preview"] = build_qt_review_apply_preview(state)
    state["guard"] = build_workspace_guard(state)
    state["flow"] = build_workspace_flow(state)
    state["ready"] = state["guard"]["problem_count"] == 0
    return state


__all__ = ["REVIEW_WORKBENCH_SCHEMA_VERSION", "build_qt_review_workbench"]
