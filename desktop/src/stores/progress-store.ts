import { create } from "zustand"
import type { ActiveJob, ProgressState } from "@/types"

interface ProgressStoreState {
  activeJobs: ActiveJob[]
}

interface ProgressStoreActions {
  addJob: (job: ActiveJob) => void
  updateJobProgress: (jobId: string, progress: ProgressState) => void
  completeJob: (jobId: string) => void
  failJob: (jobId: string, error: string) => void
  cancelJob: (jobId: string) => void
  removeJob: (jobId: string) => void
  clearCompleted: () => void
}

export const useProgressStore = create<ProgressStoreState & ProgressStoreActions>(
  (set) => ({
    activeJobs: [],

    addJob: (job) =>
      set((state) => ({ activeJobs: [...state.activeJobs, job] })),

    updateJobProgress: (jobId, progress) =>
      set((state) => ({
        activeJobs: state.activeJobs.map((j) =>
          j.job_id === jobId ? { ...j, progress } : j,
        ),
      })),

    completeJob: (jobId) =>
      set((state) => ({
        activeJobs: state.activeJobs.map((j) =>
          j.job_id === jobId ? { ...j, status: "completed" } : j,
        ),
      })),

    failJob: (jobId, error) =>
      set((state) => ({
        activeJobs: state.activeJobs.map((j) =>
          j.job_id === jobId
            ? { ...j, status: "failed", progress: { ...j.progress, message: error } }
            : j,
        ),
      })),

    cancelJob: (jobId) =>
      set((state) => ({
        activeJobs: state.activeJobs.map((j) =>
          j.job_id === jobId ? { ...j, status: "cancelled" } : j,
        ),
      })),

    removeJob: (jobId) =>
      set((state) => ({
        activeJobs: state.activeJobs.filter((j) => j.job_id !== jobId),
      })),

    clearCompleted: () =>
      set((state) => ({
        activeJobs: state.activeJobs.filter(
          (j) => j.status === "queued" || j.status === "running",
        ),
      })),
  }),
)
