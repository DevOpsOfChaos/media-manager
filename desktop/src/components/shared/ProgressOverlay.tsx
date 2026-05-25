import { useEffect, useState } from "react"
import { listen } from "@tauri-apps/api/event"
import { Loader2 } from "lucide-react"

interface OperationEvent {
  label: string
  detail?: string
}

export function ProgressOverlay() {
  const [active, setActive] = useState(false)
  const [label, setLabel] = useState("")
  const [detail, setDetail] = useState<string | null>(null)
  const [fadeOut, setFadeOut] = useState(false)

  useEffect(() => {
    const unlistenStarted = listen<OperationEvent>("operation:started", (event) => {
      setLabel(event.payload.label)
      setDetail(event.payload.detail ?? null)
      setActive(true)
      setFadeOut(false)
    })

    const unlistenCompleted = listen<OperationEvent>("operation:completed", (_event) => {
      setFadeOut(true)
      setTimeout(() => {
        setActive(false)
        setLabel("")
        setDetail(null)
        setFadeOut(false)
      }, 400)
    })

    return () => {
      unlistenStarted.then(fn => fn())
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
          {detail && (
            <p className="text-xs text-muted-foreground">{detail}</p>
          )}
        </div>
      </div>
    </div>
  )
}
