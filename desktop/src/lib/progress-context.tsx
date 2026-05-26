import { createContext, useContext, useState, useCallback, type ReactNode } from "react"

export interface ProgressState {
  active: boolean
  label: string
  current: number
  total: number
  startedAt: number
}

interface ProgressContextType {
  progress: ProgressState
  startProgress: (label: string, total: number) => void
  updateProgress: (current: number) => void
  finishProgress: () => void
}

const ProgressContext = createContext<ProgressContextType | null>(null)

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [progress, setProgress] = useState<ProgressState>({
    active: false,
    label: "",
    current: 0,
    total: 0,
    startedAt: 0,
  })

  const startProgress = useCallback((label: string, total: number) => {
    setProgress({
      active: true,
      label,
      current: 0,
      total,
      startedAt: Date.now(),
    })
  }, [])

  const updateProgress = useCallback((current: number) => {
    setProgress(prev => ({ ...prev, current }))
  }, [])

  const finishProgress = useCallback(() => {
    setProgress(prev => ({ ...prev, active: false }))
  }, [])

  return (
    <ProgressContext.Provider value={{ progress, startProgress, updateProgress, finishProgress }}>
      {children}
    </ProgressContext.Provider>
  )
}

export function useProgress() {
  const ctx = useContext(ProgressContext)
  if (!ctx) {
    return {
      progress: { active: false, label: "", current: 0, total: 0, startedAt: 0 },
      startProgress: () => {},
      updateProgress: () => {},
      finishProgress: () => {},
    } as ProgressContextType
  }
  return ctx
}
