import { useState, useEffect, useRef } from "react"
import { useT } from "@/lib/i18n"
import { Loader2, Minimize2, Maximize2, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useProgress } from "@/lib/progress-context"
import { resizeWindow, getWindowSize } from "@/lib/tauri-bridge"

export function MiniProgressOverlay() {
  const t = useT()
  const { progress } = useProgress()
  const [miniMode, setMiniMode] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [elapsedDisplay, setElapsedDisplay] = useState(0)
  const originalSize = useRef<{ w: number; h: number } | null>(null)
  const prevActive = useRef(false)

  // Track elapsed
  useEffect(() => {
    if (!progress.active) return
    const i = setInterval(() => setElapsedDisplay((Date.now() - progress.startedAt) / 1000), 1000)
    return () => clearInterval(i)
  }, [progress.active, progress.startedAt])

  // Detect completion
  useEffect(() => {
    if (prevActive.current && !progress.active) setCompleted(true)
    prevActive.current = progress.active
  }, [progress.active])

  const shrinkWindow = async () => {
    try {
      const [w, h] = await getWindowSize()
      originalSize.current = { w, h }
      await resizeWindow(400, 350)
    } catch (e) {
      console.log("Window resize not available:", e)
    }
    setMiniMode(true)
  }

  const restoreWindow = async () => {
    setMiniMode(false)
    setCompleted(false)
    try {
      if (originalSize.current) {
        await resizeWindow(originalSize.current.w, originalSize.current.h)
        originalSize.current = null
      }
    } catch {}
  }

  const pct = progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0
  const elapsed = elapsedDisplay
  const rate = progress.current / Math.max(elapsed, 0.1)
  const remaining = (progress.total - progress.current) / Math.max(rate, 0.1)
  const fmt = (s: number) => isFinite(s) && s >= 0 ? (s < 60 ? `${Math.round(s)}s` : s < 3600 ? `${Math.floor(s/60)}m` : `${Math.round(s/3600)}h`) : "—"

  // Completion card
  if (completed && !progress.active) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
        <div className="text-center space-y-4 p-8">
          <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto">
            <Check className="h-8 w-8 text-green-600" />
          </div>
          <h2 className="text-xl font-bold">{t("Complete!", "Fertig!")}</h2>
          <Button onClick={restoreWindow} size="lg" className="bg-green-600 hover:bg-green-700">
            <Maximize2 className="h-4 w-4 mr-2" />{t("Restore Window", "Fenster wiederherstellen")}
          </Button>
        </div>
      </div>
    )
  }

  if (!progress.active) return null

  // Mini mode — compact
  if (miniMode) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
        <div className="space-y-4 w-72">
          <div className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            <p className="text-sm font-medium truncate">{progress.label}</p>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${Math.max(pct, 1)}%` }} />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{pct}% · {progress.current.toLocaleString()}/{progress.total.toLocaleString()}</span>
            <span>ETA {fmt(remaining)}</span>
          </div>
          <Button variant="outline" size="sm" className="w-full" onClick={restoreWindow}>
            <Maximize2 className="h-3 w-3 mr-1" />{t("Restore", "Wiederherstellen")}
          </Button>
        </div>
      </div>
    )
  }

  // Full mode
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/95 backdrop-blur-sm">
      <div className="bg-card border border-blue-500/30 rounded-xl shadow-xl p-8 max-w-md w-full mx-4 space-y-6 text-center">
        <Loader2 className="h-10 w-10 animate-spin text-blue-400 mx-auto" />
        <h2 className="text-lg font-semibold">{progress.label}</h2>
        <div className="h-3 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${Math.max(pct, 1)}%` }} />
        </div>
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>{pct}% · {progress.current.toLocaleString()}/{progress.total.toLocaleString()}</span>
          <span>ETA {fmt(remaining)} · {fmt(elapsed)}</span>
        </div>
        <Button variant="outline" onClick={shrinkWindow}>
          <Minimize2 className="h-4 w-4 mr-2" />{t("Mini Window", "Mini-Fenster")}
        </Button>
      </div>
    </div>
  )
}
