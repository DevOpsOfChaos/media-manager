import { Loader2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { useT } from "@/lib/i18n"

interface FullPageProgressProps {
  label: string
  current: number
  total: number
  startedAt: number
}

export function FullPageProgress({ label, current, total, startedAt }: FullPageProgressProps) {
  const t = useT()
  const pct = total > 0 ? Math.round((current / total) * 100) : 0
  const elapsed = (Date.now() - startedAt) / 1000
  const rate = current / Math.max(elapsed, 0.1)
  const remaining = (total - current) / Math.max(rate, 0.1)

  const formatTime = (s: number) => {
    if (s < 60) return `${Math.round(s)}s`
    if (s < 3600) return `${Math.round(s / 60)}m ${Math.round(s % 60)}s`
    return `${Math.round(s / 3600)}h`
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/95 backdrop-blur-sm">
      <Card className="w-full max-w-md mx-4 p-8 border-blue-500/30">
        <div className="text-center space-y-6">
          <div className="flex justify-center">
            <div className="w-16 h-16 rounded-full bg-blue-500/10 flex items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            </div>
          </div>

          <div>
            <h2 className="text-lg font-semibold">{label}</h2>
            <p className="text-sm text-muted-foreground mt-1">
              {current} {t("of", "von")} {total} {t("files processed", "Dateien verarbeitet")}
            </p>
          </div>

          {/* Progress bar */}
          <div className="space-y-2">
            <div
              className="w-full h-3 bg-muted rounded-full overflow-hidden"
              role="progressbar"
              aria-valuenow={current}
              aria-valuemin={0}
              aria-valuemax={total}
            >
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${Math.max(pct, 1)}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>{pct}%</span>
              <span>{total - current} {t("remaining", "verbleibend")}</span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="p-3 rounded-lg bg-muted/30">
              <p className="text-lg font-bold">{current}</p>
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

          <p className="text-xs text-muted-foreground">
            {t("Please don't close the app during this operation.", "Bitte schließen Sie die App während dieses Vorgangs nicht.")}
          </p>
        </div>
      </Card>
    </div>
  )
}
