export type Language = "en" | "de"
export type Theme = "modern-dark" | "modern-light" | "system"
export type Density = "comfortable" | "compact"

export interface RecentPaths {
  profile_dir: string | null
  run_dir: string | null
  people_bundle_dir: string | null
  catalog: string | null
}

export interface WindowSettings {
  width: number
  height: number
  maximized: boolean
}

export interface GuiSettings {
  schema_version: string
  language: Language
  theme: Theme
  density: Density
  start_page_id: string
  confirm_before_apply: boolean
  people_privacy_acknowledged: boolean
  show_onboarding: boolean
  enable_command_palette: boolean
  recent_paths: RecentPaths
  window: WindowSettings
}
