from __future__ import annotations

from dataclasses import dataclass, field

from media_manager.core.similar_cleanup_plan import (
    SimilarCleanupPlan,
    build_similar_cleanup_plan,
)
from media_manager.execution_plan import (
    DuplicateExecutionPreview,
    ExecutionPreviewRow,
    build_duplicate_execution_preview,
)
from media_manager.execution_runner import run_duplicate_execution_preview
from media_manager.execution_safety import protect_duplicate_execution_preview
from media_manager.similar_images import SimilarImageGroup


@dataclass(slots=True)
class SimilarWorkflowBundle:
    decisions: dict[str, dict[str, str]]
    cleanup_plan: SimilarCleanupPlan
    execution_preview: DuplicateExecutionPreview = field(default_factory=lambda: DuplicateExecutionPreview(ready=False))


def _build_similar_execution_preview(plan: SimilarCleanupPlan) -> DuplicateExecutionPreview:
    preview = DuplicateExecutionPreview(ready=plan.ready_for_apply)
    for removal in plan.planned_removals:
        preview.rows.append(
            ExecutionPreviewRow(
                row_type="filesystem_delete",
                status="executable",
                group_id=removal.group_id,
                operation_mode="delete",
                source_path=removal.remove_path,
                survivor_path=removal.keep_path,
                target_path=None,
                file_size=0,
                reason="similar_image_remove_candidate",
            )
        )
    return preview


def build_similar_workflow_bundle(
    groups: list[SimilarImageGroup],
    decisions: dict[str, dict[str, str]],
) -> SimilarWorkflowBundle:
    cleanup_plan = build_similar_cleanup_plan(groups, decisions)
    execution_preview = _build_similar_execution_preview(cleanup_plan)
    execution_preview = protect_duplicate_execution_preview(execution_preview)
    return SimilarWorkflowBundle(
        decisions=decisions,
        cleanup_plan=cleanup_plan,
        execution_preview=execution_preview,
    )


def execute_similar_workflow_bundle(
    bundle: SimilarWorkflowBundle,
    *,
    apply: bool = False,
):
    return run_duplicate_execution_preview(bundle.execution_preview, apply=apply)


__all__ = [
    "SimilarWorkflowBundle",
    "build_similar_workflow_bundle",
    "execute_similar_workflow_bundle",
]
