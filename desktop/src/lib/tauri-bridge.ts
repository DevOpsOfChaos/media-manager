import { invoke } from "@tauri-apps/api/core"
import type {
  OrganizePlannerOptions,
  OrganizePreviewResponse,
  OrganizeExecutionResult,
  DuplicateScanConfig,
  DuplicatesPreviewResponse,
  SimilarImageScanConfig,
  SimilarImagesPreviewResponse,
  UndoExecutionResult,
  GuiSettings,
} from "@/types"

// ── Settings ──

/** Read current GUI settings from the settings file. */
export async function settingsRead(): Promise<GuiSettings> {
  return invoke("settings_read")
}

/** Write GUI settings to the settings file. */
export async function settingsWrite(settings: GuiSettings): Promise<GuiSettings> {
  return invoke("settings_write", { settings })
}

/** Reset GUI settings to factory defaults. */
export async function settingsReset(): Promise<GuiSettings> {
  return invoke("settings_reset")
}

// ── Organize ──

/** Preview an organize plan — scans files and builds a dry-run report without modifying anything. */
export async function organizePreview(
  options: OrganizePlannerOptions,
): Promise<OrganizePreviewResponse> {
  return invoke("organize_preview", { options })
}

/** Execute an organize plan — copies, moves, or hardlinks files according to the plan. */
export async function organizeApply(
  options: OrganizePlannerOptions,
): Promise<OrganizeExecutionResult> {
  return invoke("organize_apply", { options })
}

// ── Duplicates ──

/** Scan source directories for exact byte-level duplicate files. */
export async function duplicateScan(
  config: DuplicateScanConfig,
): Promise<DuplicatesPreviewResponse> {
  return invoke("duplicates_scan", { config })
}

/** Scan for visually similar images using perceptual hashing. */
export async function similarImagesScan(
  config: SimilarImageScanConfig,
): Promise<SimilarImagesPreviewResponse> {
  return invoke("similar_images_scan", { config })
}

/** Apply duplicate removal decisions (delete/move/copy) after review. */
export async function duplicatesApply(config: {
  source_dirs: string[]
  decisions: Record<string, string>
  mode: string
}): Promise<{ executed_rows: number; error_rows: number }> {
  return invoke("duplicates_apply", { config })
}

// ── Review Sessions ──

/** Apply review decisions: move files marked for removal to trash. */
export async function reviewApplyDecisions(options: { sessionPath: string; toKeep: Array<{path: string; decision: string}>; toRemove: string[] }): Promise<{ status: string; removed: number; errors: string[] }> {
  return invoke("review_apply_decisions", { sessionPath: options.sessionPath, toKeep: options.toKeep, toRemove: options.toRemove })
}

/** Read base64-encoded thumbnails for a batch of file paths. */
export async function readThumbnailsBatch(paths: string[]): Promise<string[]> {
  return invoke("read_thumbnails_batch", { paths })
}

/** Save review decisions as a session file for later resumption. */
export async function reviewSaveSession(payload: {
  session_path: string
  decisions: Record<string, string>
  source_kind: string
}): Promise<{ status: string; path: string; decision_count: number }> {
  return invoke("review_save_session", { payload })
}

/** Load a previously saved review session file. */
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

/** Run face recognition scan on source directories. */
export async function peopleScan(config: PeopleScanConfig): Promise<PeopleScanResult> {
  return invoke("people_scan", { config })
}

/** Check whether a previous scan cache exists for the given directories. */
export async function peopleScanStatus(options: { source_dirs: string[] }): Promise<PeopleScanStatus> {
  return invoke("people_scan_status", { options })
}

/** Reset (clear) the scan cache for given source directories. */
export async function peopleScanReset(options: { source_dirs: string[] }): Promise<{ kind: string; cleared: boolean }> {
  return invoke("people_scan_reset", { options })
}

/** Get catalog summary info (person count and names). */
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

/** List all people in the catalog with face counts. */
export async function peopleCatalogList(options: { catalog_path: string }): Promise<CatalogListResponse> {
  return invoke("people_catalog_list", { options })
}

/** Rename a person in the catalog. */
export async function peoplePersonRename(options: { catalog_path: string; person_id: string; name: string }): Promise<{ kind: string }> {
  return invoke("people_person_rename", { options })
}

/** Create a new named person in the catalog. */
export async function peoplePersonCreate(options: { catalog_path: string; name: string; aliases?: string[] }): Promise<{ kind: string; person_id: string; name: string }> {
  return invoke("people_person_create", { options })
}

/** Reassign a face from one person to another (or a new person). */
export async function peoplePersonReassign(options: { catalog_path: string; source_path: string; face_index: number; from_person_id: string; to_person_id?: string; to_person_name?: string }): Promise<{ kind: string }> {
  return invoke("people_person_reassign", { options })
}

/** Merge two person entries, combining embeddings and aliases. */
export async function peoplePersonMerge(options: {
  catalog_path: string
  from_person_id: string
  to_person_id: string
}): Promise<{ kind: string; from_person_id: string; from_name: string; to_person_id: string; to_name: string; merged_embeddings: number; new_face_count: number }> {
  return invoke("people_person_merge", { options })
}

/** Add, remove, or list ignored faces. */
export async function peopleFaceIgnore(options: {
  action: "add" | "remove" | "list"
  face_id: string
  catalog_dir: string
}): Promise<{
  kind: string
  action?: string
  face_id?: string
  added?: boolean
  removed?: boolean
  ignored_faces?: string[]
  count?: number
}> {
  return invoke("people_face_ignore", { options })
}

/** Estimate the age bracket for a detected face. */
export async function peopleFaceAge(options: {
  image_path: string
  face_box: [number, number, number, number]
}): Promise<{
  kind: string
  age_bracket: string
  confidence: number
  note?: string
  image_path: string
}> {
  return invoke("people_face_age", { options })
}

/** Record user feedback on face recognition matches to improve accuracy. */
export async function peopleFaceFeedback(options: {
  type: "confirm_match" | "reject_match" | "confirm_new_person"
  person_id: string
  face_id: string
  catalog_dir: string
}): Promise<{
  kind: string
  status: string
  stats: { total_feedback: number; confirmations: number; rejections: number }
}> {
  return invoke("people_face_feedback", { options })
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

/** List all available run history entries. */
export async function historyList(): Promise<HistoryListPayload> {
  return invoke("history_list")
}

/** Get detailed information for a specific run by ID. */
export async function historyGet(runId: string): Promise<HistoryDetail> {
  return invoke("history_get", { runId })
}

// ── Undo ──

/** Preview undo operations from a journal file without executing them. */
export async function undoPreview(
  journalPath: string,
): Promise<UndoExecutionResult> {
  return invoke("undo_preview", { journalPath })
}

/** Execute undo operations from a journal file, reversing prior changes. */
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
  gpu?: {
    cuda: boolean
    openvino: boolean
    opencv_dnn: boolean
    opencv_version: string | null
    recommendation: string
  }
  system?: {
    cpu_count: number | null
    disk_free_gb: number | null
    disk_total_gb: number | null
  }
  exiftool_version?: string | null
}

/** Collect runtime diagnostics: Python version, imports, settings, GPU support. */
export async function runtimeDiagnostics(): Promise<RuntimeDiagnostics> {
  return invoke("runtime_diagnostics")
}

// ── Rename ──

export interface RenamePreviewResponse {
  kind: string
  planned_count: number
  skipped_count: number
  conflict_count: number
  error_count: number
  entries: Array<{ source_path: string; target_path: string | null; status: string }>
}

export interface RenameApplyResponse {
  kind: string
  planned_count: number
  renamed_count: number
  skipped_count: number
  error_count: number
  conflict_count: number
}

/** Preview a rename plan without renaming files. */
export async function renamePreview(options: {
  source_dir: string
  pattern?: string
  recursive?: boolean
  include_hidden?: boolean
  follow_symlinks?: boolean
  include_patterns?: string[]
  exclude_patterns?: string[]
  date_source?: string
}): Promise<RenamePreviewResponse> {
  return invoke("rename_preview", { options })
}

/** Execute a rename plan, applying file renames. */
export async function renameApply(options: {
  source_dir: string
  pattern?: string
  recursive?: boolean
}): Promise<RenameApplyResponse> {
  return invoke("rename_apply", { options })
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

/** Preview a trip collection plan without moving files. */
export async function tripPreview(options: TripOptions): Promise<TripPreviewResponse> {
  return invoke("trip_preview", { options })
}

/** Execute a trip collection plan (copies or hardlinks files). */
export async function tripApply(options: TripOptions): Promise<TripApplyResponse> {
  return invoke("trip_apply", { options })
}

// ── Library ──

export interface LibraryBrowseResult {
  kind: string
  root: string
  file_count: number
  depth: number
  quick?: boolean
  files: Array<{ path: string; name: string; relative: string; size: number; suffix: string }>
}

/** Quick browse a directory for media file count (no metadata). */
export async function libraryBrowse(options: { root_dir: string; max_depth?: number; quick?: boolean }): Promise<LibraryBrowseResult> {
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

/** Run preflight checks on source/target directories and return a diagnostic report. */
export async function doctorCheck(options: {
  command?: string
  source_dirs: string[]
  target_root?: string
  recursive?: boolean
}): Promise<DoctorReport> {
  return invoke("doctor_check", { options })
}

// ── Library Browse (paginated) ──

export interface LibraryBrowsePaginatedResult {
  kind: string
  root: string
  file_count: number
  other_count: number
  page: number
  page_size: number
  total_pages: number
  depth: number
  cached?: boolean
  quick?: boolean
  files: Array<{
    path: string
    name: string
    relative: string
    size: number
    suffix: string
    modified: string
    category: "photo" | "video" | "raw" | "audio"
    sidecars: Array<{ path: string; name: string; relative: string; suffix: string; size: number }>
  }>
  applied_filters: {
    date_from: string | null
    date_to: string | null
    file_types: string[] | null
  }
}

/** Browse a directory with pagination support, returning detailed file metadata. */
export async function libraryBrowsePaginated(options: {
  root_dir: string
  page?: number
  page_size?: number
  max_depth?: number
  date_from?: string
  date_to?: string
  file_types?: string[]
}): Promise<LibraryBrowsePaginatedResult> {
  return invoke("library_browse", { options })
}

// ── Magic Bytes ──

export interface MagicDetectResult {
  path: string
  mime_type: string
  category: "photo" | "video" | "audio" | "raw" | "unknown"
  description: string
  confidence: number
  detected_by: string
  extension?: string
  mismatch?: boolean
  warning?: string
}

/** Detect file type by reading magic bytes (ignores extension). */
export async function magicDetect(path: string): Promise<MagicDetectResult> {
  return invoke("magic_detect", { options: { path } })
}

export interface MagicScanResult {
  real_media: Array<{ path: string; name: string; type: string }>
  fake_media: Array<{ path: string; name: string; reason: string }>
  total_scanned: number
  real_count: number
  fake_count: number
}

/** Scan directory for real media files (by content, not extension). */
export async function magicScanMedia(sourceDir: string, maxFiles?: number): Promise<MagicScanResult> {
  return invoke("magic_scan_media", { options: { source_dir: sourceDir, max_files: maxFiles ?? 1000 } })
}

// ── File Operations ──

/** Open a file with the system default application. */
export async function fileOpen(path: string): Promise<{ status: string; path: string }> {
  return invoke("file_open", { options: { path } })
}

/** Reveal a file in the system file explorer. */
export async function fileReveal(path: string): Promise<{ status: string; path: string }> {
  return invoke("file_reveal", { options: { path } })
}

/** Move a file to the trash. */
export async function fileDelete(path: string): Promise<{ status: string; path: string }> {
  return invoke("file_delete", { options: { path } })
}

/** Rename a file to a new name within the same directory. */
export async function fileRename(path: string, newName: string): Promise<{ status: string; old_path: string; new_path: string; new_name: string }> {
  return invoke("file_rename", { options: { path, new_name: newName } })
}

/** Resize and export an image to a new file. */
export async function fileExport(source: string, target: string, width: number, quality: number): Promise<{ status: string; source: string; target: string; width: number; height: number }> {
  return invoke("file_export", { options: { source, target, width, quality } })
}

export interface IntegrityCheckEntry {
  path: string
  size?: number
}

export interface IntegrityCheckResult {
  status: string
  total_checked: number
  missing_count: number
  size_changed_count: number
  missing: Array<{ path: string; expected_size?: number }>
  size_changed: Array<{ path: string; expected_size?: number; actual_size?: number }>
  healthy: boolean
}

/** Check whether files from a previously saved file list still exist and have the same size. */
export async function fileIntegrity(paths: IntegrityCheckEntry[]): Promise<IntegrityCheckResult> {
  return invoke("file_integrity", { options: { paths } })
}

export interface BackupResult {
  status: string
  path: string
  size_mb: number
  timestamp: string
}

/** Create a ZIP backup of the media-manager data directory. */
export async function fileBackup(): Promise<BackupResult> {
  return invoke("file_backup", { options: {} })
}

// ── Contact Sheet ──

export interface ContactSheetOptions {
  paths: string[]
  output: string
  title?: string
  cols?: number
  thumb_size?: number
}

export interface ContactSheetResult {
  status: string
  output: string
  images: number
  cols: number
  rows: number
}

/** Generate a contact sheet PDF from a list of image paths. */
export async function fileContactSheet(options: ContactSheetOptions): Promise<ContactSheetResult> {
  return invoke("file_contact_sheet", { options })
}

// ── Web Gallery ──

export interface WebGalleryOptions {
  paths: string[]
  output_dir: string
  title?: string
  thumb_size?: number
}

export interface WebGalleryResult {
  status: string
  output_dir: string
  index: string
  images: number
}

/** Generate a static HTML photo gallery from a list of image paths. */
export async function fileWebGallery(options: WebGalleryOptions): Promise<WebGalleryResult> {
  return invoke("file_web_gallery", { options })
}

// ── Watermark ──

export interface WatermarkOptions {
  source: string
  target: string
  text?: string
  position?: string
  opacity?: number
  font_size?: number
}

export interface WatermarkResult {
  status: string
  source: string
  target: string
}

/** Add a text watermark to an image. */
export async function fileWatermark(options: WatermarkOptions): Promise<WatermarkResult> {
  return invoke("file_watermark", { options })
}

// ── Window ──

/** Resize the application window to the given dimensions. */
export async function resizeWindow(width: number, height: number): Promise<void> {
  return invoke("resize_window", { width, height })
}

/** Get the current window size as [width, height]. */
export async function getWindowSize(): Promise<[number, number]> {
  return invoke("get_window_size")
}

// ── Enrich ──

export interface EnrichedExif {
  camera?: string
  lens?: string
  iso?: number
  aperture?: string
  shutter?: string
  focal_length?: string
  date_taken?: string
  orientation?: string
  software?: string
  megapixels?: number
}

export interface EnrichedFile {
  path: string
  file: { size: number; modified: string; extension: string }
  exif?: EnrichedExif
  gps?: { lat: string; lon: string; alt?: string } | null
  faces?: Array<{ person_id: string; name: string; box?: { x: number; y: number; w: number; h: number } }>
  colors?: string[] | null
  has_duplicates?: boolean
  auto_tags?: string[]
  magic_type?: string
  magic_mismatch?: boolean
}

/** Fetch all enriched metadata (EXIF, GPS, faces, colors, duplicates) for a single file. */
export async function enrichFile(path: string): Promise<EnrichedFile> {
  return invoke("enrich_file", { options: { path } })
}

/** Fetch enriched metadata for a batch of files (max 100). */
export async function enrichBatch(paths: string[]): Promise<{ files: EnrichedFile[]; total_requested: number; returned: number }> {
  return invoke("enrich_batch", { options: { paths } })
}

// ── Autostart ──

/** Check whether the app is configured to auto-start with Windows. */
export async function getAutostartStatus(): Promise<boolean> {
  return invoke("get_autostart_status")
}

/** Enable or disable auto-start with Windows. */
export async function setAutostart(options: { enable: boolean }): Promise<void> {
  return invoke("set_autostart", { enable: options.enable })
}

// ── Statistics ──

export interface LibraryStats {
  total_files: number
  total_size_bytes: number
  by_extension: Record<string, number>
  by_camera: Record<string, number>
  by_year: Record<string, number>
  by_month: Record<string, number>
  oldest_file: { path: string; name: string } | null
  newest_file: { path: string; name: string } | null
}

export interface SizeReport {
  largest_files: Array<{ path: string; name: string; size_bytes: number }>
  total_size_bytes: number
  file_count: number
  duplicate_space_wasted_bytes: number
}

export interface SearchResult {
  query: string
  results: Array<{ path: string; name: string; score: number; size_bytes?: number; camera?: string | null; date?: string | null }>
  total_matches: number
}

/** Compute comprehensive library statistics for a source directory. */
export async function libraryStats(options: { source_dir: string; sample_limit?: number }): Promise<LibraryStats> {
  return invoke("library_stats", { options })
}

/** Generate a size report showing largest files and duplicate space waste. */
export async function sizeReport(options: { source_dir: string; top_n?: number }): Promise<SizeReport> {
  return invoke("size_report", { options })
}

/** Full-text search across filenames, paths, camera model, and dates. */
export async function mediaSearch(options: { source_dir: string; query: string; fields?: string[]; max_results?: number }): Promise<SearchResult> {
  return invoke("media_search", { options })
}

// ── Background Scan ──

export interface BackgroundScanResult {
  status: string
  new_files: string[]
  modified_files: string[]
  deleted_files: string[]
  total_scanned: number
  total_new: number
  total_modified: number
  total_deleted: number
  scan_duration_seconds: number
  message?: string
}

/** Run an incremental background scan for new or modified files. */
export async function backgroundScan(options: { source_dirs: string[] }): Promise<BackgroundScanResult> {
  return invoke("background_scan", { config: options })
}

// ── File Health ──

export interface FileHealthResult {
  path: string
  healthy: boolean
  issues: string[]
  warnings: string[]
  detected_type?: string
}

export interface DirectoryHealthScanResult {
  total_scanned: number
  healthy_count: number
  unhealthy_count: number
  health_score: number
  issues: FileHealthResult[]
}

/** Check the health of a single media file (magic bytes, truncation, min size). */
export async function healthCheckFile(path: string): Promise<FileHealthResult> {
  return invoke("health_check_file", { path })
}

/** Scan a directory and report file health issues for all media files. */
export async function healthScanDirectory(options: {
  source_dir: string
  max_files?: number
}): Promise<DirectoryHealthScanResult> {
  return invoke("health_scan_directory", { options })
}

// ── Smart Albums ──

export interface SmartAlbumSuggestion {
  type: string
  name: string
  start?: string
  end?: string
  camera?: string
  file_count: number
  confidence: number
}

export interface SmartAlbumsResult {
  suggestions: SmartAlbumSuggestion[]
}

/** Analyze file metadata and suggest smart album groupings (date clusters, camera). */
export async function smartAlbumsSuggest(options: {
  source_dir: string
  max_files?: number
}): Promise<SmartAlbumsResult> {
  return invoke("smart_albums_suggest", { options })
}
