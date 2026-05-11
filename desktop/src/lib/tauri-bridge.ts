import { invoke } from "@tauri-apps/api/core"
import type {
  OrganizePlannerOptions,
  OrganizeDryRun,
  OrganizeExecutionResult,
  DuplicateScanConfig,
  DuplicateScanResult,
  RunSummary,
  UndoExecutionResult,
  GuiSettings,
} from "@/types"

// ── Settings ──

export async function settingsRead(): Promise<GuiSettings> {
  return invoke("settings_read")
}

export async function settingsWrite(settings: GuiSettings): Promise<GuiSettings> {
  return invoke("settings_write", { settings })
}

export async function settingsReset(): Promise<GuiSettings> {
  return invoke("settings_reset")
}

// ── Python Bridge ──

export async function runPythonCli(
  command: string,
  args: string[],
): Promise<unknown> {
  return invoke("run_python_cli", { command, args })
}

export async function readRunArtifact(
  runDir: string,
  artifactName: string,
): Promise<unknown> {
  return invoke("read_run_artifact", { runDir, artifactName })
}

export async function listRuns(): Promise<RunSummary[]> {
  return invoke("list_runs")
}

export async function getPythonInfo(): Promise<unknown> {
  return invoke("get_python_info")
}

// ── Organize ──

export async function organizePreview(
  options: OrganizePlannerOptions,
): Promise<OrganizeDryRun> {
  return invoke("organize_preview", { options })
}

export async function organizeApply(
  plan: OrganizeDryRun,
): Promise<OrganizeExecutionResult> {
  return invoke("organize_apply", { plan })
}

// ── Duplicates ──

export async function duplicateScan(
  config: DuplicateScanConfig,
): Promise<DuplicateScanResult> {
  return invoke("duplicates_scan", { config })
}

// ── People ──

export async function peopleScan(config: {
  source_dirs: string[]
}): Promise<unknown> {
  return invoke("people_scan", { config })
}

// ── History ──

export async function runsList(): Promise<RunSummary[]> {
  return invoke("runs_list")
}

export async function runsInspect(runId: string): Promise<unknown> {
  return invoke("runs_inspect", { runId })
}

// ── Undo ──

export async function undoPreview(
  journalPath: string,
): Promise<UndoExecutionResult> {
  return invoke("undo_preview", { journalPath })
}

export async function undoApply(
  journalPath: string,
): Promise<UndoExecutionResult> {
  return invoke("undo_apply", { journalPath })
}

// ── Doctor ──

export async function doctorCheck(): Promise<unknown> {
  return invoke("doctor_check")
}
