import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { useProgress } from "@/lib/progress-context"
import { useSimulatedProgress } from "@/lib/use-simulated-progress"
import { organizePreview, organizeApply } from "@/lib/tauri-bridge"
import { userFriendlyError } from "@/lib/error-utils"
import { WizardContainer } from "@/components/shared/WizardContainer"
import { SourceDetector } from "@/components/shared/SourceDetector"
import { PreCheckPanel } from "@/components/shared/PreCheckPanel"
import { ExecutionProgress } from "@/components/shared/ExecutionProgress"
import { PageHeader } from "@/components/layout/PageHeader"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip"
import { Zap, Check, RotateCcw, FolderSync, Heart, Coffee, ChevronRight } from "lucide-react"
import type { OrganizePlannerOptions, OrganizePreviewResponse, OrganizeExecutionResult } from "@/types"
import type { DateSource } from "@/types/organizer"

const PRESETS = [
  { id: "ymd", label: "Year / Month / Day", labelDe: "Jahr / Monat / Tag", pattern: "{year}/{month_name}/{day}",
    example: "2026/May/26/IMG.jpg", desc: "Best for most users", descDe: "Beste Wahl" },
  { id: "ym", label: "Year / Month", labelDe: "Jahr / Monat", pattern: "{year}/{year_month}",
    example: "2026/2026-05/IMG.jpg", desc: "Simpler", descDe: "Einfacher" },
  { id: "flat", label: "Year-Month-Day", labelDe: "Jahr-Monat-Tag", pattern: "{year}-{month}-{day}",
    example: "2026-05-26/IMG.jpg", desc: "Flat folders", descDe: "Flache Ordner" },
  { id: "camera", label: "Camera / Date", labelDe: "Kamera / Datum", pattern: "{camera}/{year}/{month_name}",
    example: "iPhone/2026/May/IMG.jpg", desc: "By camera", descDe: "Nach Kamera" },
]

const TOKENS = [
  { token: "{year}", label: "2026" }, { token: "{month}", label: "05" },
  { token: "{month_name}", label: "May" }, { token: "{month_name_de}", label: "Mai" },
  { token: "{day}", label: "26" }, { token: "{year_month}", label: "2026-05" },
  { token: "{year_month_day}", label: "2026-05-26" }, { token: "{camera}", label: "iPhone" },
]

const ORG_PHASES = [
  { nameEn: "Scanning files...", nameDe: "Dateien werden gescannt...", endAt: 15, increment: 0.5 },
  { nameEn: "Reading dates...", nameDe: "Daten werden gelesen...", endAt: 50, increment: 0.3 },
  { nameEn: "Building plan...", nameDe: "Plan wird erstellt...", endAt: 98, increment: 0.2 },
]

function buildOptions(
  sourceDir: string,
  targetDir: string,
  pattern: string,
  operationMode: "copy" | "move" | "link",
  cleanupEmpty: boolean,
  dateSource: string,
): OrganizePlannerOptions {
  return {
    source_dirs: [sourceDir],
    target_root: targetDir,
    pattern,
    recursive: true,
    include_hidden: false,
    follow_symlinks: false,
    operation_mode: operationMode,
    exiftool_path: null,
    include_associated_files: true,
    conflict_policy: "rename",
    cleanup_empty_dirs: cleanupEmpty,
    include_patterns: [],
    exclude_patterns: [],
    batch_size: 500,
    date_source: dateSource as DateSource,
  }
}

export default function OrganizePage() {
  const t = useT()
  const navigate = useNavigate()
  const { startProgress: startGlobal, updateProgress: updateGlobal, finishProgress: finishGlobal } = useProgress()
  const { phase, progress, log, start: startSim, complete: completeSim } = useSimulatedProgress(ORG_PHASES)

  const [preview, setPreview] = useState<OrganizePreviewResponse | null>(null)
  const [result, setResult] = useState<OrganizeExecutionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [executing, setExecuting] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const defaultTarget = localStorage.getItem("default_source_dir") || ""

  const [sourceDir, setSourceDir] = useState("")
  const [targetDir, setTargetDir] = useState(defaultTarget)

  const [pattern, setPattern] = useState("{year}/{month_name}/{day}")
  const [customPattern, setCustomPattern] = useState(false)

  const [operationMode, setOperationMode] = useState<"copy" | "move" | "link">("link")
  const [cleanupEmpty, setCleanupEmpty] = useState(true)
  const [dateSource, setDateSource] = useState("auto")

  const runPreview = async (): Promise<boolean> => {
    setLoading(true); setError(null)
    startSim()
    try {
      const r = await organizePreview(buildOptions(sourceDir, targetDir, pattern, operationMode, cleanupEmpty, dateSource))
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
    startGlobal(t("Organizing...", "Organisiere..."), preview?.planned_count || 100)
    try {
      const r = await organizeApply(buildOptions(sourceDir, targetDir, pattern, operationMode, cleanupEmpty, dateSource))
      updateGlobal(100)
      setResult(r)
      setShowSuccess(true)
    } catch (e) {
      setError(userFriendlyError(e).message || String(e))
    } finally {
      setTimeout(() => finishGlobal(), 500)
      setExecuting(false)
    }
  }

  const startOver = () => {
    setShowSuccess(false); setPreview(null); setResult(null)
    setError(null)
  }

  if (showSuccess && result) {
    return (
      <div className="max-w-xl mx-auto p-6 text-center space-y-6">
        <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto">
          <Check className="h-10 w-10 text-green-600" />
        </div>
        <h2 className="text-xl font-bold">{t("Organization complete!", "Organisation abgeschlossen!")}</h2>
        <p className="text-muted-foreground">
          {result.linked_count ? `${result.linked_count} files linked` : `${result.copied_count || result.moved_count} files processed`}
        </p>
        <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20">
          <CardContent className="p-4 space-y-3">
            <Heart className="h-6 w-6 text-red-500 mx-auto" fill="currentColor" />
            <p className="text-sm">{t("Enjoying Media Manager?", "Gefällt dir Media Manager?")}</p>
            <div className="flex gap-2 justify-center">
              <a href="https://www.paypal.com/" target="_blank"><Button size="sm"><Coffee className="h-3 w-3 mr-1" />{t("Donate", "Spenden")}</Button></a>
              <a href="https://github.com/mries/media-manager" target="_blank"><Button variant="outline" size="sm">Star</Button></a>
            </div>
          </CardContent>
        </Card>
        <div className="flex gap-2 justify-center">
          <Button variant="outline" onClick={startOver}><RotateCcw className="h-4 w-4 mr-1" />{t("Organize more", "Weitere organisieren")}</Button>
          <Button onClick={() => navigate("/library")}>{t("View Library", "Bibliothek ansehen")}<ChevronRight className="h-4 w-4 ml-1" /></Button>
        </div>
      </div>
    )
  }

  if (executing) {
    return (
      <div className="max-w-xl mx-auto p-6">
        <PageHeader title={t("Organizing files...", "Dateien werden organisiert...")} />
        <ExecutionProgress
          phase={phase} totalPhases={3} progress={progress} log={log}
          fileCount={preview?.planned_count || 0} etaSeconds={0}
          onMiniMode={() => { /* trigger mini mode */ }}
          toolName="organize"
        />
      </div>
    )
  }

  return (
    <WizardContainer
      steps={[
        { id: "source", label: "Select source", labelDe: "Quelle wählen" },
        { id: "pattern", label: "Folder structure", labelDe: "Ordnerstruktur" },
        { id: "options", label: "Options", labelDe: "Optionen" },
        { id: "execute", label: "Execute", labelDe: "Ausführen" },
      ]}
    >
      {({ step, goNext, goBack, footer }) => (
        <>
          {step === 0 && (
            <>
              <div className="text-center mb-6">
                <FolderSync className="h-12 w-12 text-primary mx-auto mb-3" />
                <h2 className="text-xl font-bold">{t("Organize your media", "Medien organisieren")}</h2>
                <p className="text-sm text-muted-foreground mt-1">{t("Automatically sort photos into dated folders by EXIF date.", "Sortiere Fotos automatisch in datierte Ordner nach EXIF-Datum.")}</p>
              </div>
              <SourceDetector value={sourceDir} onChange={setSourceDir} targetValue={targetDir} onTargetChange={setTargetDir} />
              <div className="mt-6">
                <Button className="w-full" size="lg" onClick={goNext} disabled={!sourceDir || !targetDir}>
                  {t("Next: Pattern", "Weiter: Muster")} <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
              {footer}
            </>
          )}

          {step === 1 && (
            <>
              <h2 className="text-lg font-semibold mb-4">{t("Choose folder structure", "Ordnerstruktur wählen")}</h2>
              <div className="grid grid-cols-2 gap-3">
                {PRESETS.map(p => (
                  <button key={p.id} onClick={() => { setPattern(p.pattern); setCustomPattern(false) }}
                    className={`text-left p-3 rounded-lg border-2 transition-all ${
                      pattern === p.pattern && !customPattern ? "border-primary bg-primary/5 ring-1 ring-primary/20" : "border-border hover:border-primary/30"
                    }`}>
                    <p className="text-sm font-medium">{t(p.label, p.labelDe)}</p>
                    <p className="text-[10px] text-muted-foreground">{t(p.desc, p.descDe)}</p>
                    <code className="text-[10px] text-primary/70 bg-muted px-1.5 py-0.5 rounded mt-1 inline-block">{p.example}</code>
                  </button>
                ))}
              </div>
              <button onClick={() => setCustomPattern(!customPattern)}
                className={`w-full mt-3 text-left p-3 rounded-lg border-2 transition-all ${customPattern ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"}`}>
                <span className="text-sm font-medium">{t("Custom pattern", "Eigenes Muster")}</span>
                {customPattern && (
                  <div className="mt-2 space-y-2">
                    <Input value={pattern} onChange={e => setPattern(e.target.value)} className="text-xs font-mono" />
                    <div className="flex flex-wrap gap-1">
                      {TOKENS.map(tk => (
                        <button key={tk.token} onClick={() => setPattern(p => p + tk.token)}
                          className="text-[10px] px-1.5 py-0.5 rounded bg-muted hover:bg-primary/10 border font-mono">{tk.token}</button>
                      ))}
                    </div>
                  </div>
                )}
              </button>
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

              <PreCheckPanel sourceDirs={[sourceDir]} targetRoot={targetDir} />

              <div className="mt-4 space-y-4">
                <div>
                  <label className="text-sm font-medium">{t("Operation mode", "Operationsmodus")}</label>
                  <div className="flex gap-3 mt-1">
                    {(["copy", "move", "link"] as const).map(mode => (
                      <Tooltip key={mode}>
                        <TooltipTrigger asChild>
                          <label className={`flex-1 text-center p-2 rounded-lg border cursor-pointer transition-all ${operationMode === mode ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"}`}>
                            <input type="radio" className="sr-only" checked={operationMode === mode} onChange={() => setOperationMode(mode)} />
                            <span className="text-sm font-medium">{mode === "copy" ? t("Copy", "Kopieren") : mode === "move" ? t("Move", "Verschieben") : t("Hardlinks", "Hardlinks")}</span>
                          </label>
                        </TooltipTrigger>
                        <TooltipContent side="bottom" className="max-w-[200px]">
                          {mode === "link" ? t("Instant, no extra space", "Sofort, kein Extra-Speicher") : ""}
                        </TooltipContent>
                      </Tooltip>
                    ))}
                  </div>
                </div>

                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" checked={cleanupEmpty} onChange={e => setCleanupEmpty(e.target.checked)} />
                  {t("Remove empty folders after", "Leere Ordner danach entfernen")}
                </label>

                <div>
                  <label className="text-sm font-medium">{t("Date source", "Datumsquelle")}</label>
                  <select value={dateSource} onChange={e => setDateSource(e.target.value)}
                    className="w-full mt-1 text-sm border rounded px-3 py-2 bg-background">
                    <option value="auto">{t("Auto (EXIF > file date)", "Auto (EXIF > Dateidatum)")}</option>
                    <option value="exif">{t("EXIF only", "Nur EXIF")}</option>
                    <option value="filename">{t("Filename only", "Nur Dateiname")}</option>
                    <option value="mtime">{t("File date only", "Nur Dateidatum")}</option>
                  </select>
                </div>
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
                <Card className="text-center p-3"><p className="text-xl font-bold">{((preview.scan_summary?.total_size_bytes || 0) / 1e9).toFixed(1)} GB</p><p className="text-[10px] text-muted-foreground">{t("Size", "Größe")}</p></Card>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={goBack}>{t("Back", "Zurück")}</Button>
                <Button className="flex-1" onClick={runApply} size="lg">
                  <Check className="h-4 w-4 mr-2" /> {t(`Apply — ${preview.planned_count} files`, `Ausführen — ${preview.planned_count} Dateien`)}
                </Button>
              </div>
              {footer}
            </>
          )}
        </>
      )}
    </WizardContainer>
  )
}
