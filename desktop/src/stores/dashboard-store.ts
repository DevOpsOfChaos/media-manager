import { create } from "zustand"
import type { RunSummary, GuiSettings } from "@/types"

interface DashboardState {
  lastScanStats: {
    total_files: number
    total_size_bytes: number
    images_count: number
    videos_count: number
    audio_count: number
    organized_count: number
    subdirectories: number
  } | null
  recentRuns: RunSummary[]
  settings: GuiSettings | null
  loading: boolean
  error: string | null
}

interface DashboardActions {
  setScanStats: (stats: DashboardState["lastScanStats"]) => void
  setRecentRuns: (runs: RunSummary[]) => void
  setSettings: (settings: GuiSettings) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useDashboardStore = create<DashboardState & DashboardActions>((set) => ({
  lastScanStats: null,
  recentRuns: [],
  settings: null,
  loading: false,
  error: null,

  setScanStats: (stats) => set({ lastScanStats: stats }),
  setRecentRuns: (runs) => set({ recentRuns: runs }),
  setSettings: (settings) => set({ settings }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
