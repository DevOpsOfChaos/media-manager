import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Loader2, Minimize2, Maximize2, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useProgress } from "@/lib/progress-context"

export function MiniProgressOverlay() {
  const t = useT()
  const { progress, setMiniMode, finishProgress } = useProgress()
  const [dismissed, setDismissed] = useState(false)
  const [elapsedDisplay, setElapsedDisplay] = useState(0)

  useEffect(() => {
    if (!progress.active) return
    const interval = setInterval(() => {
      setElapsedDisplay((Date.now() - progress.startedAt) / 1000)
    }, 1000)
    return () => clearInterval(interval)
  }, [progress.active, progress.startedAt])

  if (!progress.active || dismissed) return null

  const pct = progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0
  const elapsed = elapsedDisplay || (Date.now() - progress.startedAt) / 1000
  const rate = progress.current / Math.max(elapsed, 0.1)
  const remaining = (progress.total - progress.current) / Math.max(rate, 0.1)

  const formatTime = (s: number) => {
    if (s < 60) return `${Math.round(s)}s`
    if (s < 3600) return `${Math.round(Math.floor(s / 60))}:${String(Math.round(s % 60)).padStart(2, "0")}`
    return `${Math.round(s / 3600)}h`
  }

  if (progress.miniMode) {
    return (
      <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-right">
        <div className="bg-card border rounded-xl shadow-xl p-4 min-w-[280px] max-w-[340px] space-y-3">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <Loader2 className="h-4 w-4 animate-spin text-primary shrink-0" />
              <p className="text-sm font-medium truncate">{progress.label}</p>
            </div>
            <div className="flex items-center gap-0.5 shrink-0">
              <Button variant="ghost" size="icon" className="h-6 w-6"
                onClick={() => setMiniMode(false)}
                title={t("Expand", "Vergrößern")}>
                <Maximize2 className="h-3 w-3" />
              </Button>
              <Button variant="ghost" size="icon" className="h-6 w-6"
                onClick={() => { setDismissed(true); finishProgress() }}
                title={t("Dismiss", "Ausblenden")}>
                <X className="h-3 w-3" />
              </Button>
            </div>
          </div>

          <div className="space-y-1">
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full transition-all duration-500"
                style={{ width: `${Math.max(pct, 1)}%` }} />
            </div>
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>{pct}%</span>
              <span>{progress.current}/{progress.total}</span>
            </div>
          </div>

          <div className="flex justify-between text-[10px] text-muted-foreground">
            <span>{t("ETA", "VSL")}: {formatTime(remaining)}</span>
            <span>{t("Elapsed", "Dauer")}: {formatTime(elapsed)}</span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/95 backdrop-blur-sm">
      <div className="bg-card border border-blue-500/30 rounded-xl shadow-xl p-8 max-w-md w-full mx-4 space-y-6">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
          </div>
        </div>

        <div className="text-center">
          <h2 className="text-lg font-semibold">{progress.label}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {progress.current} {t("of", "von")} {progress.total} {t("files processed", "Dateien verarbeitet")}
          </p>
        </div>

        <div className="space-y-2">
          <div className="h-3 bg-muted rounded-full overflow-hidden" role="progressbar"
            aria-valuenow={progress.current} aria-valuemin={0} aria-valuemax={progress.total}>
            <div className="h-full bg-blue-500 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${Math.max(pct, 1)}%` }} />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{pct}%</span>
            <span>{progress.total - progress.current} {t("remaining", "verbleibend")}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="p-3 rounded-lg bg-muted/30">
            <p className="text-lg font-bold">{progress.current}</p>
            <p className="text-[10px] text-muted-foreground">{t("Done", "Fertig")}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted/30">
            <p className="text-lg font-bold">{formatTime(remaining)}</p>
            <p className="text-[10px] text-muted-foreground">{t("ETA", "VSL")}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted/30">
            <p className="text-lg font-bold">{formatTime(elapsed)}</p>
            <p className="text-[10px] text-muted-foreground">{t("Elapsed", "Verstrichen")}</p>
          </div>
        </div>

        <div className="flex justify-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setMiniMode(true)}>
            <Minimize2 className="h-4 w-4 mr-2" />
            {t("Mini Mode", "Mini-Modus")}
          </Button>
        </div>

        <p className="text-xs text-muted-foreground text-center">
          {t("You can switch to Mini Mode to free up your screen while this runs.",
             "Du kannst in den Mini-Modus wechseln, um den Bildschirm freizugeben.")}
        </p>
      </div>
    </div>
  )
}
