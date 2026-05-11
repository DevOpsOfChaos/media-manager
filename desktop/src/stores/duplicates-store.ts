import { create } from "zustand"
import type { DuplicateScanConfig, DuplicateScanResult, ExactDuplicateGroup } from "@/types"

export const defaultDuplicateConfig: DuplicateScanConfig = {
  source_dirs: [],
  recursive: true,
  include_hidden: false,
  follow_symlinks: false,
  media_extensions: null,
  include_patterns: [],
  exclude_patterns: [],
  min_file_size_bytes: 0,
}

interface DuplicatesState {
  config: DuplicateScanConfig
  result: DuplicateScanResult | null
  selectedGroups: ExactDuplicateGroup[]
  loading: boolean
  error: string | null
}

interface DuplicatesActions {
  setConfig: (config: Partial<DuplicateScanConfig>) => void
  setResult: (result: DuplicateScanResult | null) => void
  setSelectedGroups: (groups: ExactDuplicateGroup[]) => void
  toggleGroup: (group: ExactDuplicateGroup) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

export const useDuplicatesStore = create<DuplicatesState & DuplicatesActions>(
  (set) => ({
    config: { ...defaultDuplicateConfig },
    result: null,
    selectedGroups: [],
    loading: false,
    error: null,

    setConfig: (config) =>
      set((state) => ({ config: { ...state.config, ...config } })),
    setResult: (result) => set({ result, selectedGroups: [] }),
    setSelectedGroups: (groups) => set({ selectedGroups: groups }),
    toggleGroup: (group) =>
      set((state) => {
        const exists = state.selectedGroups.some(
          (g) => g.full_digest === group.full_digest,
        )
        return {
          selectedGroups: exists
            ? state.selectedGroups.filter(
                (g) => g.full_digest !== group.full_digest,
              )
            : [...state.selectedGroups, group],
        }
      }),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    reset: () =>
      set({
        config: { ...defaultDuplicateConfig },
        result: null,
        selectedGroups: [],
        loading: false,
        error: null,
      }),
  }),
)
