import { convertFileSrc } from "@tauri-apps/api/core"

const MAX_PATH_LENGTH = 260
const INVALID_CHARS = /[\x00-\x1f<>:"|?*]/g

export function safeConvertFileSrc(path: string): string | null {
  if (!path || path.length === 0) return null
  if (path.length > MAX_PATH_LENGTH) return null
  if (INVALID_CHARS.test(path)) return null

  try {
    return convertFileSrc(path)
  } catch {
    return null
  }
}
