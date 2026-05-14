export interface DuplicateScanConfig {
  source_dirs: string[]
  include_patterns: string[]
  exclude_patterns: string[]
}

export interface ExactDuplicateGroup {
  files: string[]
  file_size: number
  sample_digest: string
  full_digest: string
  same_name: boolean
  same_suffix: boolean
  extension_summary: Record<string, number>
  media_kind_summary: Record<string, number>
}

export interface DuplicatesPreviewResponse {
  kind: "preview"
  scanned_files: number
  size_candidate_groups: number
  size_candidate_files: number
  sampled_files: number
  hashed_files: number
  exact_groups: ExactDuplicateGroup[]
  exact_duplicate_files: number
  exact_duplicates: number
  errors: number
  skipped_filtered_files: number
  extension_summary: Record<string, number>
  media_kind_summary: Record<string, number>
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
  hash_size: number
  max_distance: number
  max_images: number
  max_pairs: number
  include_patterns: string[]
  exclude_patterns: string[]
}

export interface SimilarImageScanResult {
  scanned_files: string[]
  groups: SimilarImageGroup[]
  errors: string[]
}

export interface SimilarImagesPreviewResponse {
  kind: "preview"
  scanned_files: number
  image_files: number
  hashed_files: number
  candidate_pairs_checked: number
  exact_hash_pairs: number
  similar_pairs: number
  similar_groups: SimilarImageGroup[]
  errors: number
  decode_errors: number
  skipped_filtered_files: number
  guardrail?: {
    blocked: boolean
    reason: string
    image_count: number
    max_images: number
    estimated_pairs?: number
    max_pairs?: number
  }
}
