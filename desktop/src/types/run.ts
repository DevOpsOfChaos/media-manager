export interface CommandRunLog {
  command_name: string
  argv: string[]
  apply_requested: boolean
  exit_code: number
  created_at_utc: string
  run_dir: string
}

export interface RunSummary {
  run_id: string
  run_dir: string
  command_name: string
  created_at_utc: string
  apply_requested: boolean
  exit_code: number | null
}

export interface UndoEntryResult {
  source_path: string
  target_path: string | null
  action: string
  outcome: string
  reason: string
}

export interface UndoExecutionResult {
  apply_requested: boolean
  journal_path: string
  journal_command_name: string
  original_apply_requested: boolean
  original_exit_code: number | null
  entry_count: number
  reversible_entry_count: number
  planned_count: number
  undone_count: number
  skipped_count: number
  error_count: number
  entries: UndoEntryResult[]
}

export interface ExecutionJournal {
  journal_path: string
  command_name: string
  created_at_utc: string
  entries: JournalEntry[]
}

export interface JournalEntry {
  source_path: string
  target_path: string
  action: "copy" | "move" | "delete" | "rename"
  outcome: string
  reason: string
  reversible: boolean
}
