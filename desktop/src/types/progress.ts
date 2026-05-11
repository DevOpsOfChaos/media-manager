export interface ProgressPhase {
  name: string
  start_pct: number
  end_pct: number
}

export type ProgressCallback = (
  phase_name: string,
  overall_pct: number,
  message: string,
  elapsed: number,
  eta: number,
) => void

export interface ProgressState {
  phase_name: string
  overall_pct: number
  message: string
  elapsed: number
  eta: number
}

export interface ActiveJob {
  job_id: string
  job_type: string
  label: string
  started_at: string
  progress: ProgressState
  cancellable: boolean
  status: "queued" | "running" | "completed" | "failed" | "cancelled"
}
