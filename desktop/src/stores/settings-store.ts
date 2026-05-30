import { create } from "zustand"
import type { GuiSettings } from "@/types"
import { settingsRead, settingsWrite, settingsReset } from "@/lib/tauri-bridge"

export const STORAGE_KEYS = {
  libraryRoot: "library_root",
  defaultSourceDir: "default_source_dir",
  theme: "theme",
  language: "language",
  sidebarConfig: "sidebar_config",
  sidebarFavorites: "sidebar_favorites",
  smartCollections: "smart_collections",
  libraryFlags: "library_flags",
  libraryTags: "library_tags",
  libraryRatings: "library_ratings",
  recentlyViewed: "recently_viewed",
  lastBackup: "last_backup_date",
  dryRun: "dry_run",
  onboardingComplete: "onboarding_complete",
  quickSetupDone: "quick_setup_done",
  hasLaunchedBefore: "has_launched_before",
  organizeState: "organize_state",
  toolFavorites: "tool_favorites",
} as const

export const defaultSettings: GuiSettings = {
  schema_version: "1.1",
  language: "en",
  theme: "modern-dark",
  density: "comfortable",
  start_page_id: "dashboard",
  confirm_before_apply: true,
  people_privacy_acknowledged: false,
  show_onboarding: true,
  enable_command_palette: true,
  recent_paths: {
    profile_dir: null,
    run_dir: null,
    people_bundle_dir: null,
    catalog: null,
  },
  window: {
    width: 1400,
    height: 900,
    maximized: false,
  },
}

interface SettingsState {
  settings: GuiSettings
  loaded: boolean
  loading: boolean
  error: string | null
  dirty: boolean
  saved: boolean
}

interface SettingsActions {
  setSettings: (settings: GuiSettings) => void
  updateSettings: (updates: Partial<GuiSettings>) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  markClean: () => void
  markSaved: () => void
  load: () => Promise<void>
  save: () => Promise<void>
  reset: () => Promise<void>
}

export const useSettingsStore = create<SettingsState & SettingsActions>(
  (set, get) => ({
    settings: { ...defaultSettings },
    loaded: false,
    loading: false,
    error: null,
    dirty: false,
    saved: false,

    setSettings: (settings) => set({ settings, dirty: false, saved: false }),
    updateSettings: (updates) =>
      set((state) => ({
        settings: { ...state.settings, ...updates },
        dirty: true,
        saved: false,
      })),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error }),
    markClean: () => set({ dirty: false }),
    markSaved: () => set({ saved: true, dirty: false }),

    load: async () => {
      set({ loading: true, error: null })
      try {
        const settings = await settingsRead()
        set({ settings, loaded: true, loading: false, dirty: false, saved: false })
      } catch (err) {
        trackError("settings.load", err)
        set({ error: String(err), loaded: true, loading: false })
      }
    },

    save: async () => {
      const { settings } = get()
      set({ loading: true, error: null })
      try {
        const saved = await settingsWrite(settings)
        set({ settings: saved, loading: false, dirty: false, saved: true })
      } catch (err) {
        trackError("settings.save", err)
        set({ error: String(err), loading: false })
      }
    },

    reset: async () => {
      set({ loading: true, error: null })
      try {
        const settings = await settingsReset()
        set({ settings, loading: false, dirty: false, saved: true })
      } catch (err) {
        trackError("settings.reset", err)
        set({ error: String(err), loading: false })
      }
    },
  }),
)
