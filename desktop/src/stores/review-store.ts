import { create } from "zustand"
import type { ReviewSourceKind, ReviewGroup, ReviewDecisionDraft } from "@/types"
import { reviewSaveSession, reviewLoadSession } from "@/lib/tauri-bridge"
import { trackError } from "@/lib/error-tracker"

interface ReviewState {
  groups: ReviewGroup[]
  activeSourceKind: ReviewSourceKind | null
  selectedGroupId: string | null
  selectedCandidateId: string | null
  filterText: string
  sessionPath: string | null
  persistError: string | null

  setGroups: (groups: ReviewGroup[]) => void
  setActiveSourceKind: (kind: ReviewSourceKind | null) => void
  selectGroup: (groupId: string | null) => void
  selectCandidate: (candidateId: string | null) => void
  setFilterText: (text: string) => void
  setSessionPath: (path: string) => void
  setDraftDecision: (candidateId: string, decision: ReviewDecisionDraft) => void
  markReviewed: (candidateId: string) => void
  persist: () => Promise<void>
  restore: () => Promise<boolean>
  reset: () => void
}

function initialState() {
  return {
    groups: [] as ReviewGroup[],
    activeSourceKind: null as ReviewSourceKind | null,
    selectedGroupId: null as string | null,
    selectedCandidateId: null as string | null,
    filterText: "",
    sessionPath: null as string | null,
    persistError: null as string | null,
  }
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  ...initialState(),

  setGroups: (groups) => {
    set({ groups, selectedGroupId: null, selectedCandidateId: null })
    const { sessionPath } = get()
    if (sessionPath) {
      get().restore()
    }
  },

  setActiveSourceKind: (kind) =>
    set({ activeSourceKind: kind, selectedGroupId: null, selectedCandidateId: null }),

  selectGroup: (groupId) =>
    set({ selectedGroupId: groupId, selectedCandidateId: null }),

  selectCandidate: (candidateId) => set({ selectedCandidateId: candidateId }),

  setFilterText: (filterText) => set({ filterText }),

  setSessionPath: (sessionPath) => set({ sessionPath }),

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
    get().persist()
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

  persist: async () => {
    const { groups, sessionPath, activeSourceKind } = get()
    if (!sessionPath) return
    const decisions: Record<string, string> = {}
    for (const g of groups) {
      for (const c of g.candidates) {
        if (c.draft_decision !== "undecided") {
          decisions[c.id] = c.draft_decision
        }
      }
    }
    if (Object.keys(decisions).length === 0) return
    try {
      await reviewSaveSession({
        session_path: sessionPath,
        decisions,
        source_kind: activeSourceKind ?? "exact_duplicates",
      })
      set({ persistError: null })
    } catch (err) {
      trackError("reviewstore.persist", err)
      set({ persistError: String(err) })
    }
  },

  restore: async () => {
    const { sessionPath } = get()
    if (!sessionPath) return false
    try {
      const data = await reviewLoadSession({ session_path: sessionPath })
      const stored = data.decisions ?? {}
      const { groups } = get()
      set({
        groups: groups.map((g) => ({
          ...g,
          candidates: g.candidates.map((c) => {
            const decision = stored[c.id] as ReviewDecisionDraft | undefined
            if (decision && decision !== "undecided") {
              return { ...c, draft_decision: decision, role: "reviewed" as const }
            }
            return c
          }),
        })),
        persistError: null,
      })
      return true
    } catch (err) {
      trackError("reviewstore.restore", err)
      return false
    }
  },

  reset: () => set(initialState()),
}))
