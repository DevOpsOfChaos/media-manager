import { create } from "zustand"
import type { GuiSettings } from "@/types"
import { settingsRead, settingsWrite, settingsReset } from "@/lib/tauri-bridge"

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
        set({ settings, loading: false, dirty: false, saved: false })
      } catch (err) {
        set({ error: String(err), loading: false })
      }
    },

    save: async () => {
      const { settings } = get()
      set({ loading: true, error: null })
      try {
        const saved = await settingsWrite(settings)
        set({ settings: saved, loading: false, dirty: false, saved: true })
      } catch (err) {
        set({ error: String(err), loading: false })
      }
    },

    reset: async () => {
      set({ loading: true, error: null })
      try {
        const settings = await settingsReset()
        set({ settings, loading: false, dirty: false, saved: true })
      } catch (err) {
        set({ error: String(err), loading: false })
      }
    },
  }),
)
