import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ProgressBlock } from "@/components/shared/ProgressBlock"
import { Minimize2, Zap } from "lucide-react"

interface ExecutionProgressProps {
  phase: number
  totalPhases: number
  progress: number
  log: string[]
  fileCount: number
  etaSeconds: number
  onMiniMode: () => void
  toolName: string
}

const TOOL_TIPS: Record<string, Array<{ en: string; de: string }>> = {
  organize: [
    { en: "Hardlinks are instant and use no extra disk space!", de: "Hardlinks sind sofort und brauchen keinen Extra-Speicher!" },
    { en: "Large libraries (>50k files) benefit most from the date pre-filter.", de: "Große Bibliotheken (>50k) profitieren am meisten vom Datums-Vorfilter." },
    { en: "You can pause and resume operations anytime.", de: "Du kannst Operationen jederzeit pausieren und fortsetzen." },
  ],
  duplicates: [
    { en: "Exact duplicates are 100% identical — safe to delete.", de: "Exakte Duplikate sind 100% identisch — gefahrlos löschbar." },
    { en: "Use the date filter to drastically speed up scanning.", de: "Nutze den Datums-Filter für drastisch schnelleres Scannen." },
    { en: "Review results while the scan continues.", de: "Ergebnisse prüfen während der Scan weiterläuft." },
  ],
  rename: [
    { en: "EXIF dates are the most accurate for photos.", de: "EXIF-Daten sind am genauesten für Fotos." },
    { en: "Preview shows OLD → NEW before any changes.", de: "Die Vorschau zeigt ALT → NEU vor jeder Änderung." },
  ],
  trip: [
    { en: "Hardlinks let you organize without using extra space.", de: "Hardlinks organisieren ohne Extra-Speicher." },
    { en: "Set a date range to collect photos from specific trips.", de: "Setze einen Zeitraum für Fotos von bestimmten Reisen." },
  ],
}

export function ExecutionProgress({ phase, totalPhases, progress, log, fileCount, etaSeconds, onMiniMode, toolName }: ExecutionProgressProps) {
  const t = useT()
  const [tipIndex, setTipIndex] = useState(0)
  const tips = TOOL_TIPS[toolName] || TOOL_TIPS.organize

  useEffect(() => {
    const timer = setInterval(() => setTipIndex(i => (i + 1) % tips.length), 8000)
    return () => clearInterval(timer)
  }, [tips.length])

  const formatEta = (s: number) => {
    if (!isFinite(s) || s < 0) return "\u2014"
    if (s < 60) return `${Math.round(s)}s`
    if (s < 3600) return `${Math.round(s / 60)}min`
    return `${Math.round(s / 3600)}h ${Math.round((s % 3600) / 60)}min`
  }

  const showMiniRecommendation = fileCount > 1000 || etaSeconds > 120

  return (
    <div className="space-y-4">
      <ProgressBlock phase={phase} totalPhases={totalPhases} progress={progress} log={log} />

      <div className="grid grid-cols-3 gap-2">
        <Card className="text-center p-3">
          <p className="text-lg font-bold">{fileCount.toLocaleString()}</p>
          <p className="text-[10px] text-muted-foreground">{t("Files", "Dateien")}</p>
        </Card>
        <Card className="text-center p-3">
          <p className="text-lg font-bold">{formatEta(etaSeconds)}</p>
          <p className="text-[10px] text-muted-foreground">{t("Remaining", "Verbleibend")}</p>
        </Card>
        <Card className="text-center p-3">
          <p className="text-lg font-bold">{phase}/{totalPhases}</p>
          <p className="text-[10px] text-muted-foreground">{t("Phase", "Phase")}</p>
        </Card>
      </div>

      <Card className="border-blue-200 bg-blue-50/30 dark:bg-blue-950/10">
        <CardContent className="p-3 flex items-start gap-2">
          <Zap className="h-4 w-4 text-blue-500 mt-0.5 shrink-0" />
          <p className="text-xs text-blue-700 dark:text-blue-400">{t(tips[tipIndex].en, tips[tipIndex].de)}</p>
        </CardContent>
      </Card>

      {showMiniRecommendation && (
        <Card className="border-purple-200 bg-purple-50/30 dark:bg-purple-950/10">
          <CardContent className="p-4 text-center space-y-3">
            <Minimize2 className="h-8 w-8 text-purple-500 mx-auto" />
            <p className="text-sm font-medium text-purple-700 dark:text-purple-400">
              {t("Mini Mode Recommended", "Mini-Modus empfohlen")}
            </p>
            <p className="text-xs text-purple-600 dark:text-purple-400">
              {t("Shrink the window to a compact progress card while this runs in the background.", "Verkleinere das Fenster auf eine kompakte Fortschrittskarte während dies im Hintergrund läuft.")}
            </p>
            <Button variant="default" size="sm" onClick={onMiniMode} className="bg-purple-600 hover:bg-purple-700">
              <Minimize2 className="h-4 w-4 mr-1.5" /> {t("Enable Mini Mode", "Mini-Modus aktivieren")}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
