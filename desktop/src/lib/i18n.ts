import { useSettingsStore } from "@/stores/settings-store"

type Lang = "en" | "de"

export function useT() {
  const lang = (useSettingsStore((s) => s.settings?.language) || "en") as Lang
  return (en: string, de: string) => (lang === "de" ? de : en)
}
