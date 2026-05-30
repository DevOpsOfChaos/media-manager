import { trackError } from "@/lib/error-tracker"

import { STORAGE_KEYS } from "@/stores/settings-store"

export interface ToolFavorites {
  [toolId: string]: Record<string, any>
}

export function loadFavorites(): ToolFavorites {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEYS.toolFavorites) || "{}")
  } catch (e) { trackError("favorites.load", e); return {} }
}

export function saveFavorite(toolId: string, settings: Record<string, any>) {
  const favorites = loadFavorites()
  favorites[toolId] = settings
  localStorage.setItem(STORAGE_KEYS.toolFavorites, JSON.stringify(favorites))
}

export function loadFavorite(toolId: string): Record<string, any> | null {
  const favorites = loadFavorites()
  return favorites[toolId] || null
}

export function hasFavorite(toolId: string): boolean {
  return !!loadFavorite(toolId)
}
