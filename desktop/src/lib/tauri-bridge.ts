import { invoke } from "@tauri-apps/api/core"
import type {
  OrganizePlannerOptions,
  OrganizePreviewResponse,
  OrganizeExecutionResult,
  DuplicateScanConfig,
  DuplicatesPreviewResponse,
  SimilarImageScanConfig,
  SimilarImagesPreviewResponse,
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
  options: OrganizePlannerOptions,
): Promise<OrganizeExecutionResult> {
  return invoke("organize_apply", { options })
}

// ── Duplicates ──

export async function duplicateScan(
  config: DuplicateScanConfig,
): Promise<DuplicatesPreviewResponse> {
  return invoke("duplicates_scan", { config })
}

export async function similarImagesScan(
  config: SimilarImageScanConfig,
): Promise<SimilarImagesPreviewResponse> {
  return invoke("similar_images_scan", { config })
}

export async function duplicatesApply(config: {
  source_dirs: string[]
  decisions: Record<string, string>
  mode: string
}): Promise<{ executed_rows: number; error_rows: number }> {
  return invoke("duplicates_apply", { config })
}

// ── Review Sessions ──

export async function reviewSaveSession(payload: {
  session_path: string
  decisions: Record<string, string>
  source_kind: string
}): Promise<{ status: string; path: string; decision_count: number }> {
  return invoke("review_save_session", { payload })
}

export async function reviewLoadSession(payload: {
  session_path: string
}): Promise<{
  schema_version: number
  source_kind: string
  decisions: Record<string, string>
  decision_count: number
}> {
  return invoke("review_load_session", { payload })
}

// ── People ──

export interface PeopleScanConfig {
  source_dirs: string[]
  catalog_path?: string
  tolerance?: number
  backend?: string
  incremental?: boolean
  force_full?: boolean
}

export interface PeopleScanResult {
  kind: string
  incremental: boolean
  scanned_files: number
  skipped_files: number
  total_files: number
  total_faces: number
  matched_faces: number
  unknown_faces: number
  people_count: number
  image_count: number
  cache_path: string
  entries: Array<{ source_path: string; face_count: number; matched_count: number }>
}

export interface PeopleScanStatus {
  kind: string
  has_cache: boolean
  cache_path: string
  cached_files: number
  scan_summary: {
    total_faces: number
    matched_faces: number
    unknown_faces: number
    people_count: number
    image_count: number
  } | null
}

export interface CatalogInfo {
  kind: string
  path: string
  person_count: number
  people: Array<{ person_id: string; name: string; face_count: number }>
}

export async function peopleScan(config: PeopleScanConfig): Promise<PeopleScanResult> {
  return invoke("people_scan", { config })
}

export async function peopleScanStatus(options: { source_dirs: string[] }): Promise<PeopleScanStatus> {
  return invoke("people_scan_status", { options })
}

export async function peopleScanReset(options: { source_dirs: string[] }): Promise<{ kind: string; cleared: boolean }> {
  return invoke("people_scan_reset", { options })
}

export async function peopleCatalogInfo(options: { catalog_path: string }): Promise<CatalogInfo> {
  return invoke("people_catalog_info", { options })
}

export interface PersonEntry {
  person_id: string
  name: string
  face_count: number
  source_paths: string[]
  aliases: string[]
}

export interface CatalogListResponse {
  kind: string
  path: string
  person_count: number
  people: PersonEntry[]
}

export async function peopleCatalogList(options: { catalog_path: string }): Promise<CatalogListResponse> {
  return invoke("people_catalog_list", { options })
}

export async function peoplePersonRename(options: { catalog_path: string; person_id: string; name: string }): Promise<{ kind: string }> {
  return invoke("people_person_rename", { options })
}

export async function peoplePersonCreate(options: { catalog_path: string; name: string; aliases?: string[] }): Promise<{ kind: string; person_id: string; name: string }> {
  return invoke("people_person_create", { options })
}

export async function peoplePersonReassign(options: { catalog_path: string; source_path: string; face_index: number; from_person_id: string; to_person_id?: string; to_person_name?: string }): Promise<{ kind: string }> {
  return invoke("people_person_reassign", { options })
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

// ── Trip ──

export interface TripOptions {
  source_dirs: string[]
  target_root: string
  label: string
  start_date: string
  end_date: string
  use_hardlinks?: boolean
  recursive?: boolean
}

export interface TripPreviewResponse {
  kind: string
  planned_count: number
  matched_count: number
  skipped_count: number
  entries: Array<{ source_path: string; target_path: string | null; status: string }>
}

export interface TripApplyResponse {
  kind: string
  executed_count: number
  linked_count: number
  copied_count: number
  skipped_count: number
}

export async function tripPreview(options: TripOptions): Promise<TripPreviewResponse> {
  return invoke("trip_preview", { options })
}

export async function tripApply(options: TripOptions): Promise<TripApplyResponse> {
  return invoke("trip_apply", { options })
}

// ── Library ──

export interface LibraryBrowseResult {
  kind: string
  root: string
  file_count: number
  depth: number
  files: Array<{ path: string; name: string; relative: string; size: number; suffix: string }>
}

export async function libraryBrowse(options: { root_dir: string; max_depth?: number }): Promise<LibraryBrowseResult> {
  return invoke("library_browse", { options })
}

// ── Doctor ──

export interface DoctorReport {
  command: string
  status: string
  ready: boolean
  next_action: string
  summary: {
    error_count: number
    warning_count: number
    info_count: number
    source_count: number
    included_file_count: number
    scanned_file_count: number
  }
  diagnostics: Array<{
    code: string
    severity: "info" | "warning" | "error"
    message: string
    path: string | null
    hint: string | null
  }>
  source_previews: Array<{
    source_root: string
    exists: boolean
    is_dir: boolean
    scanned_file_count: number
    included_file_count: number
  }>
}

export async function doctorCheck(options: {
  command?: string
  source_dirs: string[]
  target_root?: string
  recursive?: boolean
}): Promise<DoctorReport> {
  return invoke("doctor_check", { options })
}
