import { invoke } from "@tauri-apps/api/core"
import type {
  OrganizePlannerOptions,
  OrganizeDryRun,
  OrganizePreviewResponse,
  OrganizeExecutionResult,
  DuplicateScanConfig,
  DuplicatesPreviewResponse,
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
): Promise<OrganizePreviewResponse> {
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
): Promise<DuplicatesPreviewResponse> {
  return invoke("duplicates_scan", { config })
}

// ── People ──

export async function peopleScan(config: {
  source_dirs: string[]
}): Promise<unknown> {
  return invoke("people_scan", { config })
}

// ── History ──

export interface HistoryListPayload {
  root_dir: string
  run_count: number
  valid_count: number
  invalid_count: number
  runs: HistoryRunEntry[]
}

export interface HistoryRunEntry {
  run_id: string
  run_dir: string
  command: string | null
  mode: "preview" | "apply" | null
  created_at_utc: string | null
  exit_code: number | null
  status: string | null
  next_action: string | null
  review_candidate_count: number
  has_ui_state: boolean
  has_plan_snapshot: boolean
  has_action_model: boolean
  action_count: number
  recommended_action_count: number
  has_journal: boolean
  valid: boolean
  missing_files: string[]
  errors: string[]
}

export interface HistoryDetail {
  run_id: string
  run_dir: string
  command: string | null
  mode: "preview" | "apply" | null
  created_at_utc: string | null
  exit_code: number | null
  status: string | null
  next_action: string | null
  summary: string | null
  command_json: Record<string, unknown> | null
  report_outcome: Record<string, unknown> | null
  has_journal: boolean
  valid: boolean
  missing_files: string[]
  errors: string[]
}

export async function historyList(): Promise<HistoryListPayload> {
  return invoke("history_list")
}

export async function historyGet(runId: string): Promise<HistoryDetail> {
  return invoke("history_get", { runId })
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

// ── Diagnostics ──

export interface RuntimeDiagnostics {
  python_exe: string
  project_root: string
  pythonpath_prepended: string
  settings_path_override: string | null
  env_hints: {
    MEDIA_MANAGER_PYTHON: string | null
    VIRTUAL_ENV: string | null
    CONDA_PREFIX: string | null
    MEDIA_MANAGER_PROJECT_ROOT: string | null
    MEDIA_MANAGER_SETTINGS_PATH: string | null
  }
  python_reachable: boolean
  python_error?: string
  python_version?: string
  media_manager_import?: { ok: boolean; error?: string }
  bridge_settings_import?: { ok: boolean; error?: string }
  settings_path?: string
  settings_file_exists?: boolean
}

export async function runtimeDiagnostics(): Promise<RuntimeDiagnostics> {
  return invoke("runtime_diagnostics")
}

// ── Doctor ──

export async function doctorCheck(): Promise<unknown> {
  return invoke("doctor_check")
}
