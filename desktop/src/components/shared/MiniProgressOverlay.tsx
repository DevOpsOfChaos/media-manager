import { useState, useEffect, useRef, useCallback } from "react"
import { useT } from "@/lib/i18n"
import { Loader2, Minimize2, Maximize2, Check, Expand } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useProgress } from "@/lib/progress-context"

// Dynamic import helper for Tauri window API (avoids build errors in browser)
async function getWindowApi() {
  try {
    const mod = await import("@tauri-apps/api/window")
    return mod
  } catch {
    return null
  }
}

export function MiniProgressOverlay() {
  const t = useT()
  const { progress, setMiniMode } = useProgress()
  const [completed, setCompleted] = useState(false)
  const [windowReady, setWindowReady] = useState(false)
  const originalSize = useRef<{ width: number; height: number } | null>(null)
  const prevActive = useRef(false)
  const prevMiniMode = useRef(false)
  const [elapsedDisplay, setElapsedDisplay] = useState(0)

  // Check if Tauri window API is available
  useEffect(() => {
    getWindowApi().then(api => {
      if (api) setWindowReady(true)
    })
  }, [])

  // Track elapsed time
  useEffect(() => {
    if (!progress.active) return
    const interval = setInterval(() => {
      setElapsedDisplay((Date.now() - progress.startedAt) / 1000)
    }, 1000)
    return () => clearInterval(interval)
  }, [progress.active, progress.startedAt])

  // Detect operation completion → show green card, auto-restore window
  useEffect(() => {
    if (prevActive.current && !progress.active) {
      setCompleted(true)
      // Auto-restore window after 4 seconds
      const timer = setTimeout(async () => {
        await restoreWindowSize()
        setCompleted(false)
      }, 4000)
      return () => clearTimeout(timer)
    }
    prevActive.current = progress.active
  }, [progress.active])

  // AUTO: When entering mini-mode, shrink the window
  useEffect(() => {
    if (!windowReady) return
    if (!prevMiniMode.current && progress.miniMode) {
      // Just entered mini-mode → auto-shrink
      shrinkWindow()
    }
    if (prevMiniMode.current && !progress.miniMode) {
      // Just left mini-mode → auto-restore
      restoreWindowSize()
    }
    prevMiniMode.current = progress.miniMode
  }, [progress.miniMode, windowReady])

  const saveOriginalSize = useCallback(async () => {
    if (originalSize.current) return
    const api = await getWindowApi()
    if (!api) return
    try {
      const win = api.getCurrentWindow()
      const size = await win.outerSize()
      originalSize.current = { width: size.width, height: size.height }
    } catch {}
  }, [])

  const shrinkWindow = useCallback(async () => {
    const api = await getWindowApi()
    if (!api) return
    await saveOriginalSize()
    try {
      const win = api.getCurrentWindow()
      await win.setSize(new api.PhysicalSize(420, 380))
      await win.center()
    } catch (e) { console.log("Window resize not available:", e) }
  }, [saveOriginalSize])

  const restoreWindowSize = useCallback(async () => {
    const api = await getWindowApi()
    if (!api || !originalSize.current) return
    try {
      const win = api.getCurrentWindow()
      await win.setSize(new api.PhysicalSize(
        originalSize.current.width,
        originalSize.current.height
      ))
      await win.center()
      originalSize.current = null
    } catch {}
  }, [])

  const handleRestoreClick = useCallback(async () => {
    setCompleted(false)
    setMiniMode(false) // This triggers the useEffect to restore
  }, [setMiniMode])

  const elapsed = elapsedDisplay

  // COMPLETED STATE — Green success card
  if (completed) {
    return (
      <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-right">
        <div className="bg-green-50 dark:bg-green-950/30 border border-green-300 dark:border-green-700 rounded-xl shadow-xl p-4 min-w-[260px] space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center shrink-0">
              <Check className="h-4 w-4 text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-green-800 dark:text-green-300">
                {t("Complete!", "Fertig!")} ✓
              </p>
              <p className="text-[10px] text-green-600 dark:text-green-400 truncate">
                {progress.label}
              </p>
            </div>
          </div>
          <Button size="sm" className="w-full bg-green-600 hover:bg-green-700 text-white"
            onClick={handleRestoreClick}>
            <Expand className="h-3.5 w-3.5 mr-1.5" />
            {t("Restore Window", "Fenster wiederherstellen")}
          </Button>
        </div>
      </div>
    )
  }

  if (!progress.active) return null

  const pct = progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0
  const rate = progress.current / Math.max(elapsed, 0.1)
  const remaining = (progress.total - progress.current) / Math.max(rate, 0.1)

  const formatTime = (s: number) => {
    if (!isFinite(s) || s < 0) return "—"
    if (s < 60) return `${Math.round(s)}s`
    if (s < 3600) return `${Math.round(Math.floor(s / 60))}:${String(Math.round(s % 60)).padStart(2, "0")}`
    if (s < 86400) return `${Math.round(Math.floor(s / 3600))}h ${Math.round((s % 3600) / 60)}m`
    return `${Math.round(s / 3600)}h`
  }

  // MINI MODE — Auto-shrunken window, fullscreen overlay
  if (progress.miniMode) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
        <div className="bg-card border rounded-xl shadow-xl p-6 max-w-sm w-full mx-4 space-y-4">
          <div className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin text-primary shrink-0" />
            <p className="text-sm font-medium truncate">{progress.label}</p>
          </div>

          <div className="space-y-2">
            <div className="h-3 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full transition-all duration-500"
                style={{ width: `${Math.max(pct, 1)}%` }} />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{pct}%</span>
              <span>{progress.current.toLocaleString()} / {progress.total.toLocaleString()}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-center text-xs">
            <div className="p-2 rounded bg-muted/30">
              <p className="font-bold">{formatTime(remaining)}</p>
              <p className="text-[10px] text-muted-foreground">{t("ETA", "VSL")}</p>
            </div>
            <div className="p-2 rounded bg-muted/30">
              <p className="font-bold">{formatTime(elapsed)}</p>
              <p className="text-[10px] text-muted-foreground">{t("Elapsed", "Dauer")}</p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="flex-1"
              onClick={() => setMiniMode(false)}>
              <Maximize2 className="h-3.5 w-3.5 mr-1.5" />
              {t("Restore", "Wiederherstellen")}
            </Button>
          </div>

        </div>
      </div>
    )
  }

  // FULL MODE — Normal centered overlay
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
            {progress.current.toLocaleString()} {t("of", "von")} {progress.total.toLocaleString()}
          </p>
        </div>

        <div className="space-y-2">
          <div className="h-3 bg-muted rounded-full overflow-hidden" role="progressbar"
            aria-valuenow={progress.current} aria-valuemin={0} aria-valuemax={progress.total}>
            <div className="h-full bg-blue-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(pct, 1)}%` }} />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{pct}%</span>
            <span>ETA: {formatTime(remaining)}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="p-3 rounded-lg bg-muted/30">
            <p className="text-lg font-bold">{progress.current.toLocaleString()}</p>
            <p className="text-[10px] text-muted-foreground">{t("Done", "Fertig")}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted/30">
            <p className="text-lg font-bold">{formatTime(remaining)}</p>
            <p className="text-[10px] text-muted-foreground">{t("ETA", "VSL")}</p>
          </div>
          <div className="p-3 rounded-lg bg-muted/30">
            <p className="text-lg font-bold">{formatTime(elapsed)}</p>
            <p className="text-[10px] text-muted-foreground">{t("Elapsed", "Dauer")}</p>
          </div>
        </div>

        <div className="flex justify-center gap-2">
          <Button variant="outline" size="sm" onClick={() => setMiniMode(true)}>
            <Minimize2 className="h-4 w-4 mr-2" />
            {t("Mini Window", "Mini-Fenster")}
          </Button>
        </div>

        <p className="text-xs text-muted-foreground text-center">
          {t("Auto-shrinks the window so you can use other programs.",
             "Verkleinert das Fenster automatisch für andere Programme.")}
        </p>

      </div>
    </div>
  )
}
