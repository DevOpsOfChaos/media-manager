const FAVORITES_KEY = "tool_favorites"

export interface ToolFavorites {
  [toolId: string]: Record<string, any>
}

export function loadFavorites(): ToolFavorites {
  try {
    return JSON.parse(localStorage.getItem(FAVORITES_KEY) || "{}")
  } catch { return {} }
}

export function saveFavorite(toolId: string, settings: Record<string, any>) {
  const favorites = loadFavorites()
  favorites[toolId] = settings
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites))
}

export function loadFavorite(toolId: string): Record<string, any> | null {
  const favorites = loadFavorites()
  return favorites[toolId] || null
}

export function hasFavorite(toolId: string): boolean {
  return !!loadFavorite(toolId)
}
