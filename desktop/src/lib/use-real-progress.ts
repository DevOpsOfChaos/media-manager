import { useState, useEffect, useCallback, useRef } from "react"
import { listen } from "@tauri-apps/api/event"
import type { ProgressEvent } from "@/types"

export interface RealProgressState {
  current: number
  total: number
  percent: number
  stage: string
  label: string
  etaSeconds: number
  elapsedSeconds: number
  logLines: string[]
}

export function useRealProgress() {
  const [state, setState] = useState<RealProgressState>({
    current: 0,
    total: 0,
    percent: 0,
    stage: "",
    label: "",
    etaSeconds: 0,
    elapsedSeconds: 0,
    logLines: [],
  })
  const activeRef = useRef(false)

  useEffect(() => {
    let unlistenProgress: (() => void) | undefined
    let unlistenStarted: (() => void) | undefined
    let unlistenCompleted: (() => void) | undefined

    const setup = async () => {
      unlistenProgress = await listen<ProgressEvent>("operation:progress", (event) => {
        const p = event.payload
        activeRef.current = true
        setState((prev) => ({
          current: p.current,
          total: p.total,
          percent: p.percent,
          stage: p.stage,
          label: p.label || prev.label,
          etaSeconds: p.eta_seconds,
          elapsedSeconds: p.elapsed_seconds,
          logLines: p.label && p.label !== prev.logLines[prev.logLines.length - 1]
            ? [...prev.logLines.slice(-10), p.label]
            : prev.logLines,
        }))
      })

      unlistenStarted = await listen<{ label: string }>("operation:started", () => {
        activeRef.current = true
        setState({
          current: 0,
          total: 0,
          percent: 0,
          stage: "",
          label: "",
          etaSeconds: 0,
          elapsedSeconds: 0,
          logLines: [],
        })
      })

      unlistenCompleted = await listen("operation:completed", () => {
        activeRef.current = false
        setState((prev) => ({
          ...prev,
          percent: 100,
          stage: "done",
        }))
      })
    }

    setup()
    return () => {
      unlistenProgress?.()
      unlistenStarted?.()
      unlistenCompleted?.()
    }
  }, [])

  const reset = useCallback(() => {
    activeRef.current = false
    setState({
      current: 0,
      total: 0,
      percent: 0,
      stage: "",
      label: "",
      etaSeconds: 0,
      elapsedSeconds: 0,
      logLines: [],
    })
  }, [])

  return { ...state, active: activeRef.current, reset }
}
