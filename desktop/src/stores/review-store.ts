/**
 * Review Workbench store — IN-MEMORY ONLY.
 *
 * Decisions are DRAFTS. Nothing is persisted to disk, written to a journal,
 * or applied to files. The store is reset when the page is left or the
 * session ends.
 */
import { create } from "zustand"
import type {
  ReviewSourceKind,
  ReviewGroup,
  ReviewDecisionDraft,
} from "@/types"

interface ReviewState {
  // ── Active session ──
  groups: ReviewGroup[]
  activeSourceKind: ReviewSourceKind | null
  selectedGroupId: string | null
  selectedCandidateId: string | null
  filterText: string

  // ── Actions ──
  setGroups: (groups: ReviewGroup[]) => void
  setActiveSourceKind: (kind: ReviewSourceKind | null) => void
  selectGroup: (groupId: string | null) => void
  selectCandidate: (candidateId: string | null) => void
  setFilterText: (text: string) => void
  setDraftDecision: (
    candidateId: string,
    decision: ReviewDecisionDraft,
  ) => void
  markReviewed: (candidateId: string) => void
  reset: () => void
}

function initialState() {
  return {
    groups: [] as ReviewGroup[],
    activeSourceKind: null as ReviewSourceKind | null,
    selectedGroupId: null as string | null,
    selectedCandidateId: null as string | null,
    filterText: "",
  }
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  ...initialState(),

  setGroups: (groups) => set({ groups, selectedGroupId: null, selectedCandidateId: null }),

  setActiveSourceKind: (kind) => set({ activeSourceKind: kind, selectedGroupId: null, selectedCandidateId: null }),

  selectGroup: (groupId) =>
    set({ selectedGroupId: groupId, selectedCandidateId: null }),

  selectCandidate: (candidateId) =>
    set({ selectedCandidateId: candidateId }),

  setFilterText: (filterText) => set({ filterText }),

  setDraftDecision: (candidateId, decision) => {
    const { groups } = get()
    set({
      groups: groups.map((g) => ({
        ...g,
        candidates: g.candidates.map((c) =>
          c.id === candidateId ? { ...c, draft_decision: decision } : c,
        ),
      })),
    })
  },

  markReviewed: (candidateId) => {
    const { groups } = get()
    set({
      groups: groups.map((g) => ({
        ...g,
        candidates: g.candidates.map((c) =>
          c.id === candidateId ? { ...c, role: "reviewed" as const } : c,
        ),
      })),
    })
  },

  reset: () => set(initialState()),
}))
