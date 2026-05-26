import { useState, useEffect, useRef } from "react"
import { useT } from "@/lib/i18n"
import { Loader2, Check, X } from "lucide-react"
import { useProgress } from "@/lib/progress-context"

export function MiniProgressOverlay() {
  const t = useT()
  const { progress, finishProgress } = useProgress()
  const [completed, setCompleted] = useState(false)
  const [dismissed, setDismissed] = useState(false)
  const prevActive = useRef(false)
  const [elapsedDisplay, setElapsedDisplay] = useState(0)

  // Track elapsed time
  useEffect(() => {
    if (!progress.active) return
    const interval = setInterval(() => {
      setElapsedDisplay((Date.now() - progress.startedAt) / 1000)
    }, 1000)
    return () => clearInterval(interval)
  }, [progress.active, progress.startedAt])

  // Detect operation completion
  useEffect(() => {
    if (prevActive.current && !progress.active) {
      setCompleted(true)
      const timer = setTimeout(() => setCompleted(false), 5000)
      return () => clearTimeout(timer)
    }
    prevActive.current = progress.active
  }, [progress.active])

  if (!progress.active && !completed) return null
  if (dismissed) return null

  const pct = progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0
  const elapsed = elapsedDisplay
  const rate = progress.current / Math.max(elapsed, 0.1)
  const remaining = (progress.total - progress.current) / Math.max(rate, 0.1)

  const formatTime = (s: number) => {
    if (!isFinite(s) || s < 0) return "—"
    if (s < 60) return `${Math.round(s)}s`
    if (s < 3600) return `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}`
    return `${Math.round(s / 3600)}h ${Math.round((s % 3600) / 60)}m`
  }

  // Completion card
  if (completed) {
    return (
      <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-right">
        <div className="bg-green-50 dark:bg-green-950/30 border border-green-300 dark:border-green-700 rounded-xl shadow-xl p-4 min-w-[240px] space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-green-500 flex items-center justify-center shrink-0">
              <Check className="h-3.5 w-3.5 text-white" />
            </div>
            <p className="text-sm font-semibold text-green-800 dark:text-green-300">{t("Complete!", "Fertig!")}</p>
          </div>
          <p className="text-[10px] text-green-600 dark:text-green-400">{progress.label}</p>
        </div>
      </div>
    )
  }

  // Progress card — compact, bottom-right, doesn't block the UI
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-card border rounded-xl shadow-xl p-4 min-w-[280px] max-w-[340px] space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <Loader2 className="h-4 w-4 animate-spin text-primary shrink-0" />
            <p className="text-sm font-medium truncate">{progress.label}</p>
          </div>
          <button onClick={() => { setDismissed(true); finishProgress() }}
            className="text-muted-foreground hover:text-foreground shrink-0">
            <X className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Progress bar */}
        <div className="space-y-1.5">
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full transition-all duration-500"
              style={{ width: `${Math.max(pct, 1)}%` }} />
          </div>
          <div className="flex justify-between text-[10px] text-muted-foreground">
            <span>{pct}%</span>
            <span>{progress.current.toLocaleString()} / {progress.total.toLocaleString()}</span>
          </div>
        </div>

        {/* Stats */}
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>ETA: {formatTime(remaining)}</span>
          <span>{formatTime(elapsed)}</span>
        </div>
      </div>
    </div>
  )
}
