import { invoke } from "@tauri-apps/api/core"

export interface PreflightResult {
  ok: boolean
  python: boolean
  exiftool: boolean
  sourceExists: boolean
  issues: string[]
}

export async function runPreflight(sourceDir?: string): Promise<PreflightResult> {
  try {
    const result = await invoke<PreflightResult>("run_preflight", { sourceDir })
    return result
  } catch {
    return {
      ok: false,
      python: false,
      exiftool: false,
      sourceExists: false,
      issues: ["Preflight check failed"],
    }
  }
}
