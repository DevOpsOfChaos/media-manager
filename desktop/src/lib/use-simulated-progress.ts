import { useState, useEffect, useRef, useCallback } from "react"

export interface PhaseDefinition {
  nameEn: string
  nameDe: string
  endAt: number
  increment: number
}

export function useSimulatedProgress(phases: PhaseDefinition[], intervalMs = 800) {
  const [phase, setPhase] = useState(0)
  const [progress, setProgress] = useState(0)
  const [log, setLog] = useState<string[]>([])
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const phasesRef = useRef(phases)
  phasesRef.current = phases

  const start = useCallback(() => {
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null }
    setPhase(0)
    setProgress(0)
    setLog([phasesRef.current[0]?.nameEn || "Starting..."])
    intervalRef.current = setInterval(() => {
      setProgress(prevProgress => {
        let nextProgress = prevProgress
        setPhase(prevPhase => {
          const defs = phasesRef.current
          if (prevPhase >= defs.length) return prevPhase
          const def = defs[prevPhase]
          nextProgress = Math.min(prevProgress + def.increment, def.endAt)
          if (nextProgress >= def.endAt && prevPhase + 1 < defs.length) {
            const next = defs[prevPhase + 1]
            setLog(l => [...l.slice(-10), next.nameEn])
            return prevPhase + 1
          }
          return prevPhase
        })
        return Math.min(nextProgress, 98)
      })
    }, intervalMs)
  }, [intervalMs])

  const complete = useCallback((finalLogEn?: string) => {
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null }
    setProgress(100)
    setPhase(phasesRef.current.length)
    if (finalLogEn) setLog(prev => [...prev.slice(-5), finalLogEn])
  }, [])

  useEffect(() => {
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [])

  return { phase, progress, log, start, complete }
}
