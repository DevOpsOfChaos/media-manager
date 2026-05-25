import { createContext, useContext, useState, useCallback, type ReactNode } from "react"

export interface ProgressState {
  active: boolean
  label: string
  current: number
  total: number
  startedAt: number
  miniMode: boolean
}

interface ProgressContextType {
  progress: ProgressState
  startProgress: (label: string, total: number) => void
  updateProgress: (current: number) => void
  finishProgress: () => void
  setMiniMode: (mini: boolean) => void
}

const ProgressContext = createContext<ProgressContextType | null>(null)

export function ProgressProvider({ children }: { children: ReactNode }) {
  const [progress, setProgress] = useState<ProgressState>({
    active: false,
    label: "",
    current: 0,
    total: 0,
    startedAt: 0,
    miniMode: false,
  })

  const startProgress = useCallback((label: string, total: number) => {
    setProgress({
      active: true,
      label,
      current: 0,
      total,
      startedAt: Date.now(),
      miniMode: false,
    })
  }, [])

  const updateProgress = useCallback((current: number) => {
    setProgress(prev => ({ ...prev, current }))
  }, [])

  const finishProgress = useCallback(() => {
    setProgress(prev => ({ ...prev, active: false }))
  }, [])

  const setMiniMode = useCallback((mini: boolean) => {
    setProgress(prev => ({ ...prev, miniMode: mini }))
  }, [])

  return (
    <ProgressContext.Provider value={{ progress, startProgress, updateProgress, finishProgress, setMiniMode }}>
      {children}
    </ProgressContext.Provider>
  )
}

export function useProgress() {
  const ctx = useContext(ProgressContext)
  if (!ctx) {
    return {
      progress: { active: false, label: "", current: 0, total: 0, startedAt: 0, miniMode: false },
      startProgress: () => {},
      updateProgress: () => {},
      finishProgress: () => {},
      setMiniMode: () => {},
    } as ProgressContextType
  }
  return ctx
}
