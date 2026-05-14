/**
 * Review Workbench data model — FRONTEND/MODEL-ONLY DRAFT.
 *
 * ALL VALUES ARE IN-MEMORY ONLY. Nothing in this file is persisted to disk,
 * written to a journal, sent to a backend apply command, or applied to files.
 *
 * This model exists to design the review workflow structure before any
 * destructive action (delete, move, apply) is implemented.
 */

// ── Source kinds ──

export type ReviewSourceKind = "exact_duplicates" | "similar_images"

// ── Candidate roles (neutral — no "delete"/"keep" implied) ──

export type ReviewCandidateRole =
  | "undecided"     // not yet reviewed
  | "reviewed"      // human has looked at it

// ── Draft decision (in-memory only, NOT persisted, NOT applied) ──

export type ReviewDecisionDraft =
  | "undecided"        // no draft decision made
  | "keep_reference"   // user intends to keep this as the reference copy
  | "remove_later"     // user intends to remove this copy later (when apply exists)
  | "ignore"           // user intends to skip this candidate

// ── Safety state per candidate ──

export interface ReviewSafetyState {
  /** Whether this candidate has associated sibling files (e.g. RAW+JPEG pairs). */
  has_associated_files: boolean
  /** Human-readable reason if the candidate cannot be safely removed. */
  blocked_reason: string | null
  /** Whether the backend safety check would allow removal (always false in preview). */
  safe_to_remove: false  // always false — apply not implemented
}

// ── A single reviewable candidate (one file in a duplicate/similar group) ──

export interface ReviewCandidate {
  /** Unique ID: hash or group_id + path. */
  id: string
  /** Full file path. */
  path: string
  /** File size in bytes. */
  size_bytes: number
  /** For similar images: Hamming distance from anchor (0 = identical hash). */
  distance: number | null
  /** For similar images: pixel dimensions. */
  width: number | null
  height: number | null
  /** Draft decision (in-memory only). */
  draft_decision: ReviewDecisionDraft
  /** Role in review workflow. */
  role: ReviewCandidateRole
  /** Safety metadata. */
  safety: ReviewSafetyState
}

// ── A review group (one exact duplicate group or similar image cluster) ──

export interface ReviewGroup {
  /** Unique group ID (hash digest for exact, anchor_path hash for similar). */
  id: string
  /** What kind of scan produced this group. */
  source_kind: ReviewSourceKind
  /** All candidates in this group. */
  candidates: ReviewCandidate[]
  /** Short label for display. */
  label: string
  /** When the preview scan was performed (ISO timestamp). */
  scanned_at_utc: string | null
  /** Group-level note. */
  note: string | null
}

// ── Unsupported reason (why a feature is not available yet) ──

export interface ReviewUnsupportedReason {
  feature: string
  reason: string
  planned: boolean
}

// ── Review workbench session (in-memory only) ──

export interface ReviewSession {
  /** Session ID (generated client-side, not persisted). */
  session_id: string
  /** When this session was created. */
  created_at_utc: string
  /** Active source kind filter. */
  active_source_kind: ReviewSourceKind | null
  /** All review groups currently loaded in memory. */
  groups: ReviewGroup[]
  /** Currently selected group ID. */
  selected_group_id: string | null
  /** Currently selected candidate ID. */
  selected_candidate_id: string | null
  /** Session source (always "memory" — no persistence). */
  storage: "memory"
}

// ── Feature availability ──

export const REVIEW_FEATURE_STATUS = {
  exact_duplicates_preview: "available" as const,
  similar_images_preview: "available" as const,
  decision_persistence: "not_implemented" as const,
  apply_decisions: "not_implemented" as const,
  journal_write: "not_implemented" as const,
  undo_execution: "not_implemented" as const,
} as const

export const UNSUPPORTED_FEATURES: ReviewUnsupportedReason[] = [
  {
    feature: "Decision persistence",
    reason: "Decision file format and write path not yet defined.",
    planned: true,
  },
  {
    feature: "Apply decisions",
    reason: "Requires journal, undo plan, preflight checks, and user confirmation.",
    planned: true,
  },
  {
    feature: "Journal write",
    reason: "Journal format exists in backend (execution_journal) but not wired to desktop.",
    planned: true,
  },
  {
    feature: "Undo execution",
    reason: "Requires journal entries and undo plan model.",
    planned: true,
  },
]
