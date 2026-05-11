export interface ScanOptions {
  source_dirs: string[]
  recursive: boolean
  include_hidden: boolean
  follow_symlinks: boolean
  media_extensions: string[] | null
  include_patterns: string[]
  exclude_patterns: string[]
}

export interface ScannedFile {
  source_root: string
  path: string
  relative_path: string
  extension: string
  size_bytes: number
}

export interface ScanSummary {
  source_dirs: string[]
  files: ScannedFile[]
  missing_sources: string[]
  skipped_hidden_paths: number
  skipped_non_media_files: number
  skipped_filtered_files: number
  source_count: number
  media_file_count: number
  total_size_bytes: number
}
