export interface DuplicateScanConfig {
  source_dirs: string[]
  recursive: boolean
  include_hidden: boolean
  follow_symlinks: boolean
  media_extensions: string[] | null
  include_patterns: string[]
  exclude_patterns: string[]
  min_file_size_bytes: number
}

export interface ExactDuplicateGroup {
  files: string[]
  file_size: number
  sample_digest: string
  full_digest: string
  same_name: boolean
  same_suffix: boolean
}

export interface DuplicateScanResult {
  scanned_files: { source_root: string; path: string; relative_path: string; extension: string; size_bytes: number }[]
  exact_groups: ExactDuplicateGroup[]
  exact_duplicate_files: string[]
  errors: string[]
  extension_summary: Record<string, number>
  media_kind_summary: Record<string, number>
}

export interface SimilarImageMember {
  path: string
  hash_hex: string
  distance: number
  width: number
  height: number
}

export interface SimilarImageGroup {
  anchor_path: string
  members: SimilarImageMember[]
}

export interface SimilarImageScanConfig {
  source_dirs: string[]
  recursive: boolean
  include_hidden: boolean
  follow_symlinks: boolean
  hash_size: number
  max_distance: number
}

export interface SimilarImageScanResult {
  scanned_files: string[]
  groups: SimilarImageGroup[]
  errors: string[]
}
