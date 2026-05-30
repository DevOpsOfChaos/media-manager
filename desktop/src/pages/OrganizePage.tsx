import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { useSimulatedProgress } from "@/lib/use-simulated-progress"
import { useOrganizeStore } from "@/stores/organize-store"
import { useProgress } from "@/lib/progress-context"
import { organizePreview, organizeApply } from "@/lib/tauri-bridge"
import { userFriendlyError } from "@/lib/error-utils"
import type { OrganizePreviewResponse, OrganizeExecutionResult } from "@/types"
import { PageHeader } from "@/components/layout/PageHeader"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip"
import { FolderOpen, FolderSync, Play, Check, ChevronRight, ChevronLeft, Loader2, Heart, Coffee, RotateCcw } from "lucide-react"
import { ProgressBlock } from "@/components/shared/ProgressBlock"

const STEPS = ["settings", "preview", "execute"] as const
type Step = typeof STEPS[number]

const PRESETS = [
  { id: "year-month-day", label: "Year / Month / Day", labelDe: "Jahr / Monat / Tag", pattern: "{year}/{month_name}/{day}", 
    example: "2026/May/26/IMG.jpg", desc: "Best for most users", descDe: "Am besten für die meisten Nutzer" },
  { id: "year-month", label: "Year / Month", labelDe: "Jahr / Monat", pattern: "{year}/{year_month}",
    example: "2026/2026-05/IMG.jpg", desc: "Simpler structure", descDe: "Einfachere Struktur" },
  { id: "flat", label: "Year-Month-Day (flat)", labelDe: "Jahr-Monat-Tag (flach)", pattern: "{year}-{month}-{day}",
    example: "2026-05-26/IMG.jpg", desc: "No year subfolders", descDe: "Keine Jahres-Unterordner" },
]

const TOKENS = [
  { token: "{year}", label: "2026" }, { token: "{month}", label: "05" },
  { token: "{month_name}", label: "May" }, { token: "{month_name_de}", label: "Mai" },
  { token: "{day}", label: "26" }, { token: "{year_month}", label: "2026-05" },
  { token: "{year_month_day}", label: "2026-05-26" },
]

export default function OrganizePage() {
  const t = useT()
  const navigate = useNavigate()
  const { options, setOptions, reset } = useOrganizeStore()
  const { startProgress, updateProgress, finishProgress } = useProgress()

  const [step, setStep] = useState<Step>("settings")
  const [preview, setPreview] = useState<OrganizePreviewResponse | null>(null)
  const [result, setResult] = useState<OrganizeExecutionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [customPattern, setCustomPattern] = useState(false)

  const ORG_PHASES = [
    { nameEn: "Phase 1/3 — Loading settings", nameDe: "Phase 1/3 — Einstellungen laden", endAt: 30, increment: 1 },
    { nameEn: "Phase 2/3 — Scanning files", nameDe: "Phase 2/3 — Dateien scannen", endAt: 70, increment: 0.5 },
    { nameEn: "Phase 3/3 — Building plan", nameDe: "Phase 3/3 — Plan erstellen", endAt: 95, increment: 0.3 },
  ]
  const { phase: scanPhase, progress: simulatedProgress, log: scanLog, start: startOrgProgress, complete: completeOrgProgress } = useSimulatedProgress(ORG_PHASES)

  const browseDir = async (target: "source" | "target") => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog")
      const selected = await open({ directory: true, multiple: false })
      if (selected && typeof selected === "string") {
        if (target === "source") setOptions({ source_dirs: [selected] })
        else setOptions({ target_root: selected })
      }
    } catch {}
  }

  const runPreview = async () => {
    const src = options.source_dirs?.[0]
    if (!src || !options.target_root) {
      setError(t("Source and target required", "Quelle und Ziel erforderlich"))
      return
    }
    setLoading(true); setError(null); setPreview(null)
    startOrgProgress()
    startProgress(t("Building preview...", "Erstelle Vorschau..."), 100)
    try {
      const r = await organizePreview(options)
      completeOrgProgress()
      updateProgress(100)
      setPreview(r)
      setStep("preview")
    } catch (e) {
      setError(userFriendlyError(e))
    } finally {
      setTimeout(() => finishProgress(), 500)
      setLoading(false)
    }
  }

  const runApply = async () => {
    if (!preview?.outcome_report?.safe_to_apply) return
    setLoading(true); setError(null)
    startProgress(t("Applying...", "Führe aus..."), preview.planned_count)
    try {
      const r = await organizeApply(options)
      updateProgress(preview.planned_count)
      setResult(r)
      setStep("execute")
      reset()
    } catch (e) {
      setError(userFriendlyError(e))
    } finally {
      setTimeout(() => finishProgress(), 500)
      setLoading(false)
    }
  }

  const startOver = () => {
    setStep("settings")
    setPreview(null)
    setResult(null)
    setError(null)
    reset()
  }

  // ── STEP 1: Settings ──
  if (step === "settings") {
    return (
      <>
        <PageHeader title={t("Organize Files", "Dateien organisieren")} />
        <main className="max-w-5xl mx-auto p-6 space-y-6">
          {/* Source */}
          <Card>
            <CardHeader><CardTitle>{t("1. Source", "1. Quelle")}</CardTitle></CardHeader>
            <CardContent className="flex gap-2">
              <Input value={options.source_dirs?.[0] || ""} onChange={e => setOptions({ source_dirs: [e.target.value] })}
                placeholder="G:\Bilder_unsortiert" className="text-sm" />
              <Button variant="outline" onClick={() => browseDir("source")} aria-label={t("Browse folder", "Ordner durchsuchen")}><FolderOpen className="h-4 w-4" /></Button>
            </CardContent>
          </Card>

          {/* Target */}
          <Card>
            <CardHeader><CardTitle>{t("2. Target", "2. Ziel")}</CardTitle></CardHeader>
            <CardContent className="flex gap-2">
              <Input value={options.target_root} onChange={e => setOptions({ target_root: e.target.value })}
                placeholder="G:\Medienspeicher" className="text-sm" />
              <Button variant="outline" onClick={() => browseDir("target")} aria-label={t("Browse folder", "Ordner durchsuchen")}><FolderSync className="h-4 w-4" /></Button>
            </CardContent>
          </Card>

          {/* Pattern */}
          <Card>
            <CardHeader>
              <CardTitle>{t("3. Pattern", "3. Muster")}</CardTitle>
              <CardDescription>{t("How should files be organized?", "Wie sollen Dateien organisiert werden?")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 gap-2">
                {PRESETS.map(p => (
                  <button key={p.id} onClick={() => { setOptions({ pattern: p.pattern }); setCustomPattern(false) }}
                    className={`text-left p-3 rounded-lg border-2 transition-all ${
                      options.pattern === p.pattern && !customPattern ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"
                    }`}>
                    <p className="text-sm font-medium">{t(p.label, p.labelDe)}</p>
                    <p className="text-xs text-muted-foreground">{t(p.desc, p.descDe)}</p>
                    <code className="text-xs text-primary/70 bg-muted px-1.5 py-0.5 rounded mt-1 inline-block">{p.example}</code>
                  </button>
                ))}
                <button onClick={() => setCustomPattern(true)}
                  className={`text-left p-3 rounded-lg border-2 transition-all ${customPattern ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"}`}>
                  <p className="text-sm font-medium">{t("Custom", "Eigenes Muster")}</p>
                  {customPattern && (
                    <div className="mt-2 space-y-2">
                      <Input value={options.pattern} onChange={e => setOptions({ pattern: e.target.value })}
                        placeholder="{year}/{month_name}/{day}" className="text-xs font-mono" />
                      <div className="flex flex-wrap gap-1">
                        {TOKENS.map(tk => (
                          <button key={tk.token} onClick={() => setOptions({ pattern: (options.pattern || "") + tk.token })}
                            className="text-xs px-1.5 py-0.5 rounded bg-muted hover:bg-primary/10 border font-mono">
                            {tk.token}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </button>
              </div>
            </CardContent>
          </Card>

          {/* Options */}
          <Card>
            <CardHeader><CardTitle>{t("4. Options", "4. Optionen")}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="flex gap-4">
                {(["copy", "link", "move"] as const).map(mode => (
                  <Tooltip key={mode}>
                    <TooltipTrigger asChild>
                      <label className="flex items-center gap-1.5 text-sm cursor-pointer">
                        <input type="radio" name="mode" checked={options.operation_mode === mode}
                          onChange={() => setOptions({ operation_mode: mode })} />
                        {mode === "copy" ? t("Copy", "Kopieren") : mode === "link" ? t("Hardlinks", "Hardlinks") : t("Move", "Verschieben")}
                      </label>
                    </TooltipTrigger>
                    <TooltipContent>
                      {mode === "copy" ? t("Keep originals, uses extra space", "Originale bleiben, braucht Extra-Speicher")
                        : mode === "link" ? t("Instant, zero extra space, one file two paths", "Sofort, null Extra-Speicher, eine Datei zwei Pfade")
                        : t("Move files, clean up source", "Dateien verschieben, Quelle aufräumen")}
                    </TooltipContent>
                  </Tooltip>
                ))}
              </div>
              <label className="flex items-center gap-2 text-xs cursor-pointer">
                <input type="checkbox" checked={options.cleanup_empty_dirs || false}
                  onChange={e => setOptions({ cleanup_empty_dirs: e.target.checked })} />
                {t("Remove empty folders after", "Leere Ordner danach entfernen")}
              </label>
              <div>
                <label className="text-xs font-medium">{t("Date source", "Datumsquelle")}</label>
                <select value={(options as any).date_source || "auto"}
                  onChange={e => setOptions({ date_source: e.target.value as any })} 
                  className="text-xs border rounded px-2 py-1 bg-background w-full mt-1">
                  <option value="auto">{t("Auto", "Auto")}</option>
                  <option value="exif">{t("EXIF metadata", "EXIF-Metadaten")}</option>
                  <option value="filename">{t("Filename", "Dateiname")}</option>
                  <option value="mtime">{t("File date", "Dateidatum")}</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {error && <p role="alert" className="text-sm text-red-500 dark:text-red-400">{error}</p>}

          {loading && (
            <ProgressBlock phase={scanPhase} totalPhases={3} progress={simulatedProgress} log={scanLog} />
          )}

          <Button onClick={runPreview} disabled={loading} className="w-full" size="lg">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {t("Preview", "Vorschau")}
          </Button>
          <p className="text-xs text-muted-foreground text-center">
            {t("Large libraries (10,000+ files) may take a few minutes.", "Große Bibliotheken (10.000+ Dateien) können einige Minuten dauern.")}
          </p>
        </main>
      </>
    )
  }

  // ── STEP 2: Preview ──
  if (step === "preview" && preview) {
    return (
      <>
        <PageHeader title={t("Preview Results", "Vorschau-Ergebnisse")}>
          <Button variant="outline" size="sm" onClick={() => setStep("settings")}>
            <ChevronLeft className="h-4 w-4 mr-1" /> {t("Back", "Zurück")}
          </Button>
        </PageHeader>
        <main className="max-w-5xl mx-auto p-6 space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-2">
            <Card className="text-center p-3"><p className="text-xl font-bold text-green-600 dark:text-green-400">{preview.planned_count.toLocaleString()}</p><p className="text-xs text-muted-foreground">{t("Planned", "Geplant")}</p></Card>
            <Card className="text-center p-3"><p className="text-xl font-bold text-amber-600 dark:text-amber-400">{preview.skipped_count.toLocaleString()}</p><p className="text-xs text-muted-foreground">{t("Skipped", "Überspr.")}</p></Card>
            <Card className="text-center p-3"><p className="text-xl font-bold text-red-600 dark:text-red-400">{preview.conflict_count.toLocaleString()}</p><p className="text-xs text-muted-foreground">{t("Conflicts", "Konflikte")}</p></Card>
            <Card className="text-center p-3"><p className="text-xl font-bold">{((preview.scan_summary?.total_size_bytes || 0) / 1e9).toFixed(1)} GB</p><p className="text-xs text-muted-foreground">{t("Size", "Größe")}</p></Card>
          </div>

          {/* File list preview (first 20) */}
          {preview.entries && preview.entries.length > 0 && (
            <Card>
              <CardHeader><CardTitle>{t("Files to organize", "Zu organisierende Dateien")} ({preview.entries.length.toLocaleString()})</CardTitle></CardHeader>
              <CardContent className="max-h-64 overflow-y-auto space-y-1">
                {preview.entries.slice(0, 20).map((e, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-1 border-b last:border-0">
                    <Badge variant={e.status === "planned" ? "default" : "secondary"} className="text-xs shrink-0">{e.status}</Badge>
                    <span className="font-mono truncate flex-1">{e.source_path?.split(/[\\/]/).pop()}</span>
                    <span className="text-muted-foreground truncate">{e.target_relative_dir || "—"}</span>
                  </div>
                ))}
                {preview.entries.length > 20 && (
                  <p className="text-xs text-muted-foreground text-center pt-1">
                    {t(`... and ${preview.entries.length - 20} more`, `... und ${preview.entries.length - 20} weitere`)}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {error && <p role="alert" className="text-sm text-red-500 dark:text-red-400">{error}</p>}

          <Button onClick={runApply} disabled={loading || !preview.outcome_report?.safe_to_apply} className="w-full" size="lg" variant="default">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Check className="h-4 w-4 mr-2" />}
            {t(`Apply — ${preview.planned_count.toLocaleString()} files`, `Ausführen — ${preview.planned_count.toLocaleString()} Dateien`)}
          </Button>
        </main>
      </>
    )
  }

  // ── STEP 3: Result ──
  if (step === "execute" && result) {
    return (
      <>
        <PageHeader title={t("Complete!", "Fertig!")} />
        <main className="max-w-5xl mx-auto p-6 space-y-6 text-center">
          {/* Success */}
          <div className="w-20 h-20 rounded-full bg-green-100 dark:bg-green-900/20 flex items-center justify-center mx-auto">
            <Check className="h-10 w-10 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold">{t("Organization complete!", "Organisation abgeschlossen!")}</h2>
            <p className="text-muted-foreground mt-1">
              {result.linked_count ? 
                t(`${result.linked_count} files linked`, `${result.linked_count} Dateien verknüpft`) :
                result.copied_count ? 
                t(`${result.copied_count} files copied`, `${result.copied_count} Dateien kopiert`) :
                t(`${result.moved_count} files moved`, `${result.moved_count} Dateien verschoben`)}
            </p>
            {result.removed_empty_dir_count ? (
              <p className="text-sm text-muted-foreground mt-1">
                + {result.removed_empty_dir_count} {t("empty folders removed", "leere Ordner entfernt")}
              </p>
            ) : null}
          </div>

          {/* Donation */}
          <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/10 border-amber-200">
            <CardContent className="p-4 space-y-3">
              <Heart className="h-6 w-6 text-red-500 dark:text-red-400 mx-auto" fill="currentColor" />
              <p className="text-sm font-medium">{t("Enjoying Media Manager?", "Gefällt dir Media Manager?")}</p>
              <p className="text-xs text-muted-foreground">
                {t("If this tool saves you time, consider supporting its development.", "Wenn dieses Tool dir Zeit spart, unterstütze die Entwicklung.")}
              </p>
              <div className="flex gap-2 justify-center">
                <a href="https://www.paypal.com/" target="_blank" rel="noopener">
                  <Button variant="default" size="sm"><Coffee className="h-3 w-3 mr-1" />{t("Donate", "Spenden")}</Button>
                </a>
                <a href="https://github.com/mries/media-manager" target="_blank" rel="noopener">
                  <Button variant="outline" size="sm">⭐ {t("Star on GitHub", "GitHub Star")}</Button>
                </a>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-2 justify-center">
            <Button onClick={startOver} variant="outline" size="sm">
              <RotateCcw className="h-4 w-4 mr-1" /> {t("Organize more", "Weitere organisieren")}
            </Button>
            <Button onClick={() => navigate("/library")} variant="default" size="sm">
              {t("View Library", "Bibliothek ansehen")} <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </main>
      </>
    )
  }

  return null
}
