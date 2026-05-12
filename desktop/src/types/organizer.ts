export type OperationMode = "copy" | "move"
export type ConflictPolicy = "conflict" | "skip"
export type EntryStatus = "planned" | "skipped" | "conflict" | "error"
export type EntryOutcome = "copied" | "moved" | "skipped" | "conflict" | "error"

export interface OrganizePlannerOptions {
  source_dirs: string[]
  target_root: string
  pattern: string
  recursive: boolean
  include_hidden: boolean
  follow_symlinks: boolean
  operation_mode: OperationMode
  exiftool_path: string | null
  include_associated_files: boolean
  conflict_policy: ConflictPolicy
  include_patterns: string[]
  exclude_patterns: string[]
  batch_size: number
}

export interface OrganizePlanEntry {
  scanned_file: {
    source_root: string
    path: string
    relative_path: string
    extension: string
    size_bytes: number
  }
  resolution: {
    path: string
    resolved_datetime: string
    resolved_value: string
    source_kind: string
    source_label: string
    confidence: "high" | "medium" | "low"
    timezone_status: string
    reason: string
    candidates_checked: number
    parseable_candidate_count: number
    unparseable_candidate_count: number
    metadata_conflict: boolean
    decision_policy: string
  } | null
  operation_mode: OperationMode
  status: EntryStatus
  reason: string
  target_relative_dir: string | null
  target_path: string | null
  source_path: string
  source_root: string
  group_id: string | null
  group_kind: string | null
}

export interface OrganizeDryRun {
  options: OrganizePlannerOptions
  scan_summary: {
    source_dirs: string[]
    files: { source_root: string; path: string; relative_path: string; extension: string; size_bytes: number }[]
    missing_sources: string[]
    skipped_hidden_paths: number
    skipped_non_media_files: number
    skipped_filtered_files: number
    source_count: number
    media_file_count: number
    total_size_bytes: number
  }
  entries: OrganizePlanEntry[]
  planned_count: number
  skipped_count: number
  conflict_count: number
  error_count: number
  missing_source_count: number
  media_file_count: number
  status_summary: Record<string, number>
  reason_summary: Record<string, number>
  resolution_source_summary: Record<string, number>
  confidence_summary: Record<string, number>
  media_group_count: number
  associated_file_count: number
}

export interface OrganizeExecutionEntry {
  plan_entry: OrganizePlanEntry
  outcome: EntryOutcome
  reason: string
  source_path: string
  target_path: string | null
}

export interface OrganizeExecutionResult {
  plan: OrganizeDryRun
  entries: OrganizeExecutionEntry[]
  processed_count: number
  copied_count: number
  moved_count: number
  executed_count: number
  skipped_count: number
  conflict_count: number
  error_count: number
  outcome_summary: Record<string, number>
  reason_summary: Record<string, number>
}

// ── Bridge preview response (from bridge_organize_preview.py) ──

export interface OrganizePreviewOutcome {
  command: string
  phase: string
  status: string
  conflict_policy: string
  safe_to_apply: boolean
  needs_review: boolean
  total_count: number
  actionable_count: number
  blocked_count: number
  review_candidate_count: number
  counts: {
    planned: number
    skipped: number
    conflict: number
    error: number
    missing_source: number
  }
  status_summary: Record<string, number>
  reason_summary: Record<string, number>
  next_action: string
}

export interface OrganizePreviewEntry {
  source_path: string
  source_root: string
  relative_source_path: string
  extension: string
  size_bytes: number
  status: EntryStatus
  reason: string
  operation_mode: OperationMode
  target_relative_dir: string | null
  target_path: string | null
  resolution: {
    path: string
    resolved_datetime: string | null
    resolved_value: string
    source_kind: string
    source_label: string
    confidence: "high" | "medium" | "low"
    timezone_status: string
    reason: string
    candidates_checked: number
  } | null
  group_id: string | null
  group_kind: string | null
  associated_file_count: number
  association_warning_count: number
}

export interface OrganizePreviewResponse {
  kind: "preview"
  dry_run: true
  options: OrganizePlannerOptions
  scan_summary: {
    source_dirs: string[]
    missing_sources: string[]
    source_count: number
    media_file_count: number
    total_size_bytes: number
  }
  planned_count: number
  skipped_count: number
  conflict_count: number
  error_count: number
  missing_source_count: number
  media_file_count: number
  media_group_count: number
  associated_file_count: number
  association_warning_count: number
  status_summary: Record<string, number>
  reason_summary: Record<string, number>
  resolution_source_summary: Record<string, number>
  confidence_summary: Record<string, number>
  group_kind_summary: Record<string, number>
  outcome_report: OrganizePreviewOutcome
  entries: OrganizePreviewEntry[]
}
