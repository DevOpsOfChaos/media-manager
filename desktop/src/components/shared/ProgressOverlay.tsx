import { useEffect, useState } from "react"
import { listen } from "@tauri-apps/api/event"
import { Loader2 } from "lucide-react"
import type { ProgressEvent } from "@/types"

interface OperationEvent {
  label: string
  detail?: string
}

export function ProgressOverlay() {
  const [active, setActive] = useState(false)
  const [label, setLabel] = useState("")
  const [detail, setDetail] = useState<string | null>(null)
  const [fadeOut, setFadeOut] = useState(false)
  const [pct, setPct] = useState(0)
  const [stageLabel, setStageLabel] = useState("")

  useEffect(() => {
    const unlistenStarted = listen<OperationEvent>("operation:started", (event) => {
      setLabel(event.payload.label)
      setDetail(event.payload.detail ?? null)
      setActive(true)
      setFadeOut(false)
      setPct(0)
      setStageLabel("")
    })

    const unlistenProgress = listen<ProgressEvent>("operation:progress", (event) => {
      const p = event.payload
      if (p.total > 0) {
        setPct(p.percent)
        setStageLabel(p.label || p.stage)
      }
    })

    const unlistenCompleted = listen<OperationEvent>("operation:completed", (_event) => {
      setPct(100)
      setFadeOut(true)
      setTimeout(() => {
        setActive(false)
        setLabel("")
        setDetail(null)
        setFadeOut(false)
        setPct(0)
        setStageLabel("")
      }, 400)
    })

    return () => {
      unlistenStarted.then(fn => fn())
      unlistenProgress.then(fn => fn())
      unlistenCompleted.then(fn => fn())
    }
  }, [])

  if (!active) return null

  return (
    <div className={`fixed bottom-4 right-4 z-50 transition-opacity duration-300 ${fadeOut ? "opacity-0" : "opacity-100"}`}>
      <div className="flex items-center gap-3 bg-card border border-border rounded-lg px-4 py-3 shadow-lg">
        <Loader2 className="w-4 h-4 animate-spin text-primary" />
        <div>
          <p className="text-sm font-medium">{label}</p>
          {stageLabel && (
            <p className="text-xs text-muted-foreground">{stageLabel}</p>
          )}
          {detail && (
            <p className="text-xs text-muted-foreground">{detail}</p>
          )}
          {pct > 0 && (
            <div className="h-1 bg-muted rounded-full mt-1 w-full overflow-hidden">
              <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${pct}%` }} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
