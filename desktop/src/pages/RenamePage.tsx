import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { useProgress } from "@/lib/progress-context"
import { useSimulatedProgress } from "@/lib/use-simulated-progress"
import { renamePreview, renameApply } from "@/lib/tauri-bridge"
import { userFriendlyError } from "@/lib/error-utils"
import { WizardContainer } from "@/components/shared/WizardContainer"
import { SourceDetector } from "@/components/shared/SourceDetector"
import { PreCheckPanel } from "@/components/shared/PreCheckPanel"
import { ExecutionProgress } from "@/components/shared/ExecutionProgress"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Check, RotateCcw, Pencil, Heart, Coffee, ChevronRight, Zap } from "lucide-react"

const TEMPLATES = [
  { id: "date-name", label: "Date + Original name", labelDe: "Datum + Originalname", pattern: "{date:%Y-%m-%d}_{stem}",
    example: "IMG_0001.jpg → 2024-05-26_IMG_0001.jpg" },
  { id: "camera-date", label: "Camera + Date + Name", labelDe: "Kamera + Datum + Name", pattern: "{camera}_{date:%Y-%m-%d}_{stem}",
    example: "IMG_0001.jpg → iPhone_2024-05-26_IMG_0001.jpg" },
  { id: "date-only", label: "Date only", labelDe: "Nur Datum", pattern: "{date:%Y%m%d}_{stem}",
    example: "IMG_0001.jpg → 20240526_IMG_0001.jpg" },
  { id: "year-date-name", label: "Year / Date + Name", labelDe: "Jahr / Datum + Name", pattern: "{date:%Y}/{date:%Y-%m-%d}_{stem}",
    example: "IMG_0001.jpg → 2024/2024-05-26_IMG_0001.jpg" },
]

const TOKENS = [
  { token: "{date:%Y-%m-%d}", label: "2024-05-26" },
  { token: "{date:%Y%m%d}", label: "20240526" },
  { token: "{date:%Y}", label: "2024" },
  { token: "{date:%B}", label: "May" },
  { token: "{stem}", label: "IMG_0001" },
  { token: "{camera}", label: "iPhone" },
  { token: "{ext}", label: ".jpg" },
]

const RENAME_PHASES = [
  { nameEn: "Scanning files...", nameDe: "Dateien werden gescannt...", endAt: 30, increment: 0.5 },
  { nameEn: "Resolving dates...", nameDe: "Daten werden aufgelöst...", endAt: 70, increment: 0.3 },
  { nameEn: "Building plan...", nameDe: "Plan wird erstellt...", endAt: 98, increment: 0.2 },
]

export default function RenamePage() {
  const t = useT()
  const navigate = useNavigate()
  const { startProgress: startGlobal, updateProgress: updateGlobal, finishProgress: finishGlobal } = useProgress()
  const { phase, progress, log, start: startSim, complete: completeSim } = useSimulatedProgress(RENAME_PHASES)

  const [preview, setPreview] = useState<any>(null)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [executing, setExecuting] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const [sourceDir, setSourceDir] = useState("")
  const [pattern, setPattern] = useState("{date:%Y-%m-%d}_{stem}")
  const [recursive, setRecursive] = useState(true)
  const [includeHidden, setIncludeHidden] = useState(false)

  const runPreview = async () => {
    setLoading(true); setError(null)
    startSim()
    try {
      const r = await renamePreview({ source_dir: sourceDir, pattern, recursive, include_hidden: includeHidden })
      completeSim()
      setPreview(r)
      return true
    } catch (e) {
      setError(userFriendlyError(e).message || String(e))
      return false
    } finally { setLoading(false) }
  }

  const runApply = async () => {
    setExecuting(true); setError(null)
    startGlobal(t("Renaming...", "Benenne um..."), preview?.planned_count || 100)
    try {
      const r = await renameApply({ source_dir: sourceDir, pattern, recursive })
      updateGlobal(100)
      setResult(r)
      setShowSuccess(true)
    } catch (e) { setError(userFriendlyError(e).message || String(e)) }
    finally { setTimeout(() => finishGlobal(), 500); setExecuting(false) }
  }

  const startOver = () => { setShowSuccess(false); setPreview(null); setResult(null); setError(null) }

  if (showSuccess && result) {
    return (
      <div className="max-w-xl mx-auto p-6 text-center space-y-6">
        <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto"><Check className="h-10 w-10 text-green-600" /></div>
        <h2 className="text-xl font-bold">{t("Renaming complete!", "Umbenennung abgeschlossen!")}</h2>
        <p className="text-muted-foreground">{result.renamed_count || 0} {t("files renamed", "Dateien umbenannt")}</p>
        <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20"><CardContent className="p-4 space-y-3">
          <Heart className="h-6 w-6 text-red-500 mx-auto" fill="currentColor" />
          <p className="text-sm">{t("Enjoying Media Manager?", "Gefällt dir Media Manager?")}</p>
          <div className="flex gap-2 justify-center">
            <a href="https://www.paypal.com/" target="_blank"><Button size="sm"><Coffee className="h-3 w-3 mr-1" />{t("Donate", "Spenden")}</Button></a>
            <a href="https://github.com/mries/media-manager" target="_blank"><Button variant="outline" size="sm">Star</Button></a>
          </div>
        </CardContent></Card>
        <div className="flex gap-2 justify-center">
          <Button variant="outline" onClick={startOver}><RotateCcw className="h-4 w-4 mr-1" />{t("Rename more", "Weitere umbenennen")}</Button>
          <Button onClick={() => navigate("/library")}>{t("View Library", "Bibliothek ansehen")}<ChevronRight className="h-4 w-4 ml-1" /></Button>
        </div>
      </div>
    )
  }

  if (executing) {
    return (
      <div className="max-w-xl mx-auto p-6">
        <ExecutionProgress phase={phase} totalPhases={3} progress={progress} log={log}
          fileCount={preview?.planned_count || 0} etaSeconds={0}
          onMiniMode={() => {}} toolName="rename" />
      </div>
    )
  }

  return (
    <WizardContainer steps={[
      { id: "source", label: "Select source", labelDe: "Quelle wählen" },
      { id: "pattern", label: "Pattern", labelDe: "Muster" },
      { id: "options", label: "Options", labelDe: "Optionen" },
      { id: "execute", label: "Execute", labelDe: "Ausführen" },
    ]}>
      {({ step, goNext, goBack, footer }) => (
        <>
          {step === 0 && (
            <>
              <div className="text-center mb-6">
                <Pencil className="h-12 w-12 text-primary mx-auto mb-3" />
                <h2 className="text-xl font-bold">{t("Rename files", "Dateien umbenennen")}</h2>
                <p className="text-sm text-muted-foreground mt-1">{t("Batch rename files using dates and metadata.", "Dateien automatisch umbenennen mit Datum und Metadaten.")}</p>
              </div>
              <SourceDetector value={sourceDir} onChange={setSourceDir} showTarget={false} />
              <div className="mt-6">
                <Button className="w-full" size="lg" onClick={goNext} disabled={!sourceDir}>
                  {t("Next: Pattern", "Weiter: Muster")} <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
              {footer}
            </>
          )}

          {step === 1 && (
            <>
              <h2 className="text-lg font-semibold mb-4">{t("Choose pattern", "Muster wählen")}</h2>
              <div className="grid grid-cols-2 gap-3">
                {TEMPLATES.map(tpl => (
                  <button key={tpl.id} onClick={() => setPattern(tpl.pattern)}
                    className={`text-left p-3 rounded-lg border-2 transition-all ${
                      pattern === tpl.pattern ? "border-primary bg-primary/5 ring-1 ring-primary/20" : "border-border hover:border-primary/30"
                    }`}>
                    <p className="text-sm font-medium">{t(tpl.label, tpl.labelDe)}</p>
                    <code className="text-[10px] text-primary/70 bg-muted px-1.5 py-0.5 rounded mt-1 inline-block">{tpl.example}</code>
                  </button>
                ))}
              </div>
              <div className="mt-3">
                <Input value={pattern} onChange={e => setPattern(e.target.value)} className="text-xs font-mono" />
                <div className="flex flex-wrap gap-1 mt-2">
                  {TOKENS.map(tk => (
                    <button key={tk.token} onClick={() => setPattern(p => p + tk.token)}
                      className="text-[10px] px-1.5 py-0.5 rounded bg-muted hover:bg-primary/10 border font-mono">{tk.token}</button>
                  ))}
                </div>
              </div>
              <div className="flex justify-between mt-6">
                <Button variant="outline" onClick={goBack}>{t("Back", "Zurück")}</Button>
                <Button onClick={goNext}>{t("Next: Options", "Weiter: Optionen")} <ChevronRight className="h-4 w-4 ml-1" /></Button>
              </div>
              {footer}
            </>
          )}

          {step === 2 && (
            <>
              <h2 className="text-lg font-semibold mb-4">{t("Options", "Optionen")}</h2>
              <PreCheckPanel sourceDirs={[sourceDir]} targetRoot="" />
              <div className="mt-4 space-y-3">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={recursive} onChange={e => setRecursive(e.target.checked)} />
                  {t("Include subfolders", "Unterordner einbeziehen")}
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={includeHidden} onChange={e => setIncludeHidden(e.target.checked)} />
                  {t("Include hidden files", "Versteckte Dateien einbeziehen")}
                </label>
              </div>
              <div className="flex gap-2 mt-6">
                <Button variant="outline" onClick={goBack}>{t("Back", "Zurück")}</Button>
                <Button className="flex-1" onClick={async () => { const ok = await runPreview(); if (ok) goNext() }} disabled={loading}>
                  {loading ? t("Scanning...", "Scanne...") : t("Preview", "Vorschau")}
                </Button>
                <Button variant="secondary" className="flex-1" onClick={runApply} disabled={!preview}>
                  <Zap className="h-4 w-4 mr-1" /> {t("Direct execute", "Direkt ausführen")}
                </Button>
              </div>
              {error && (
                <p className="text-sm text-red-600 dark:text-red-400 mt-2">{error}</p>
              )}
              {footer}
            </>
          )}

          {step === 3 && preview && (
            <>
              <h2 className="text-lg font-semibold mb-4">{t("Ready to execute", "Bereit zur Ausführung")}</h2>
              <div className="grid grid-cols-4 gap-2 mb-4">
                <Card className="text-center p-3"><p className="text-xl font-bold text-green-600">{preview.planned_count}</p><p className="text-[10px] text-muted-foreground">{t("Planned", "Geplant")}</p></Card>
                <Card className="text-center p-3"><p className="text-xl font-bold text-amber-600">{preview.skipped_count}</p><p className="text-[10px] text-muted-foreground">{t("Skipped", "Überspr.")}</p></Card>
                <Card className="text-center p-3"><p className="text-xl font-bold text-red-600">{preview.conflict_count}</p><p className="text-[10px] text-muted-foreground">{t("Conflicts", "Konflikte")}</p></Card>
                <Card className="text-center p-3"><p className="text-xl font-bold">—</p><p className="text-[10px] text-muted-foreground">{t("Errors", "Fehler")}</p></Card>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={goBack}>{t("Back", "Zurück")}</Button>
                <Button className="flex-1" onClick={runApply} size="lg">
                  <Check className="h-4 w-4 mr-2" /> {t(`Apply — ${preview.planned_count} files`, `Ausführen — ${preview.planned_count} Dateien`)}
                </Button>
              </div>
              {error && (
                <p className="text-sm text-red-600 dark:text-red-400 mt-2">{error}</p>
              )}
              {footer}
            </>
          )}
        </>
      )}
    </WizardContainer>
  )
}
