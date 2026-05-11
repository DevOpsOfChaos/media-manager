import { create } from "zustand"
import type { OrganizePlannerOptions, OrganizeDryRun, OrganizeExecutionResult } from "@/types"

export type OrganizeStep = "sources" | "config" | "preview" | "result"

export const defaultOrganizeOptions: OrganizePlannerOptions = {
  source_dirs: [],
  target_root: "",
  pattern: "{year}/{year_month_day}",
  recursive: true,
  include_hidden: false,
  follow_symlinks: false,
  operation_mode: "copy",
  exiftool_path: null,
  include_associated_files: false,
  conflict_policy: "conflict",
  include_patterns: [],
  exclude_patterns: [],
  batch_size: 0,
}

interface OrganizeState {
  step: OrganizeStep
  options: OrganizePlannerOptions
  dryRun: OrganizeDryRun | null
  result: OrganizeExecutionResult | null
  loading: boolean
  error: string | null
}

interface OrganizeActions {
  setStep: (step: OrganizeStep) => void
  setOptions: (options: Partial<OrganizePlannerOptions>) => void
  setDryRun: (dryRun: OrganizeDryRun | null) => void
  setResult: (result: OrganizeExecutionResult | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  reset: () => void
}

export const useOrganizeStore = create<OrganizeState & OrganizeActions>((set) => ({
  step: "sources",
  options: { ...defaultOrganizeOptions },
  dryRun: null,
  result: null,
  loading: false,
  error: null,

  setStep: (step) => set({ step }),
  setOptions: (options) =>
    set((state) => ({ options: { ...state.options, ...options } })),
  setDryRun: (dryRun) => set({ dryRun }),
  setResult: (result) => set({ result }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () =>
    set({
      step: "sources",
      options: { ...defaultOrganizeOptions },
      dryRun: null,
      result: null,
      loading: false,
      error: null,
    }),
}))
