import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { useProgress } from "@/lib/progress-context"
import { renamePreview, renameApply, type RenamePreviewResponse, type RenameApplyResponse } from "@/lib/tauri-bridge"
import { userFriendlyError } from "@/lib/error-utils"
import { PageHeader } from "@/components/layout/PageHeader"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { FolderOpen, Play, Check, ChevronRight, ChevronLeft, Loader2, Heart, Coffee, RotateCcw } from "lucide-react"

const STEPS = ["settings", "preview", "execute"] as const
type Step = typeof STEPS[number]

const RENAME_TEMPLATES = [
  { id: "date-stem", label: "Date + Original Name", labelDe: "Datum + Originalname", value: "{date:%Y-%m-%d}_{stem}",
    example: "2026-05-26_IMG_0001.JPG" },
  { id: "year-date-stem", label: "Year / Date + Name", labelDe: "Jahr / Datum + Name", value: "{date:%Y}/{date:%Y-%m-%d}_{stem}",
    example: "2026/2026-05-26_IMG_0001.JPG" },
  { id: "camera-date", label: "Camera + Date", labelDe: "Kamera + Datum", value: "{camera}/{date:%Y-%m-%d}_{stem}",
    example: "iPhone/2026-05-26_IMG_0001.JPG" },
  { id: "stem-only", label: "Original Name only", labelDe: "Nur Originalname", value: "{stem}",
    example: "IMG_0001.JPG" },
  { id: "date-only", label: "Date only", labelDe: "Nur Datum", value: "{date:%Y-%m-%d}",
    example: "2026-05-26.JPG" },
]

const TOKENS = [
  { token: "{date:%Y-%m-%d}", label: "2026-05-26" },
  { token: "{date:%Y}", label: "2026" },
  { token: "{date:%m}", label: "05" },
  { token: "{date:%d}", label: "26" },
  { token: "{stem}", label: "IMG_0001" },
  { token: "{ext}", label: ".JPG" },
  { token: "{camera}", label: "iPhone" },
]

export default function RenamePage() {
  const t = useT()
  const navigate = useNavigate()
  const { startProgress, updateProgress, finishProgress } = useProgress()

  const [step, setStep] = useState<Step>("settings")
  const [sourceDir, setSourceDir] = useState(() => localStorage.getItem("default_source_dir") || "")
  const [pattern, setPattern] = useState(RENAME_TEMPLATES[0].value)
  const [customPattern, setCustomPattern] = useState(false)
  const [recursive, setRecursive] = useState(true)
  const [includeHidden, setIncludeHidden] = useState(false)
  const [dateSource, setDateSource] = useState<"auto" | "exif" | "filename" | "mtime">("auto")
  const [preview, setPreview] = useState<RenamePreviewResponse | null>(null)
  const [result, setResult] = useState<RenameApplyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const browseDir = async () => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog")
      const selected = await open({ directory: true, multiple: false })
      if (selected && typeof selected === "string") {
        setSourceDir(selected)
      }
    } catch {}
  }

  const runPreview = async () => {
    if (!sourceDir) {
      setError(t("Source directory required", "Quellverzeichnis erforderlich"))
      return
    }
    setLoading(true); setError(null); setPreview(null)
    let p = 0
    const interval = setInterval(() => { p = Math.min(p + 0.5, 90); updateProgress(Math.round(p)) }, 1000)
    startProgress(t("Building rename preview...", "Erstelle Umbenennungs-Vorschau..."), 100)
    try {
      const r = await renamePreview({ source_dir: sourceDir, pattern, recursive, include_hidden: includeHidden, date_source: dateSource })
      clearInterval(interval)
      updateProgress(100)
      setPreview(r)
      setStep("preview")
    } catch (e) {
      clearInterval(interval)
      setError(userFriendlyError(e))
    } finally {
      setTimeout(() => finishProgress(), 500)
      setLoading(false)
    }
  }

  const runApply = async () => {
    if (!preview || preview.planned_count === 0) return
    setLoading(true); setError(null)
    startProgress(t("Applying...", "Führe aus..."), preview.planned_count)
    try {
      const r = await renameApply({ source_dir: sourceDir, pattern, recursive })
      updateProgress(preview.planned_count)
      setResult(r)
      setStep("execute")
      localStorage.setItem("default_source_dir", sourceDir)
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
  }

  // ── STEP 1: Settings ──
  if (step === "settings") {
    return (
      <>
        <PageHeader title={t("Rename Files", "Dateien umbenennen")} />
        <main className="max-w-2xl mx-auto p-6 space-y-6">
          {/* Source */}
          <Card>
            <CardHeader><CardTitle>{t("1. Source", "1. Quelle")}</CardTitle></CardHeader>
            <CardContent className="flex gap-2">
              <Input value={sourceDir} onChange={e => setSourceDir(e.target.value)}
                placeholder="G:\Bilder_unsortiert" className="text-sm" />
              <Button variant="outline" onClick={browseDir}><FolderOpen className="h-4 w-4" /></Button>
            </CardContent>
          </Card>

          {/* Pattern */}
          <Card>
            <CardHeader>
              <CardTitle>{t("2. Pattern", "2. Muster")}</CardTitle>
              <CardDescription>{t("How should files be renamed?", "Wie sollen Dateien umbenannt werden?")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 gap-2">
                {RENAME_TEMPLATES.map(p => (
                  <button key={p.id} onClick={() => { setPattern(p.value); setCustomPattern(false) }}
                    className={`text-left p-3 rounded-lg border-2 transition-all ${
                      pattern === p.value && !customPattern ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"
                    }`}>
                    <p className="text-sm font-medium">{t(p.label, p.labelDe)}</p>
                    <code className="text-[10px] text-primary/70 bg-muted px-1.5 py-0.5 rounded mt-1 inline-block">{p.example}</code>
                  </button>
                ))}
                <button onClick={() => setCustomPattern(true)}
                  className={`text-left p-3 rounded-lg border-2 transition-all ${customPattern ? "border-primary bg-primary/5" : "border-border hover:border-primary/30"}`}>
                  <p className="text-sm font-medium">{t("Custom", "Eigenes Muster")}</p>
                  {customPattern && (
                    <div className="mt-2 space-y-2">
                      <Input value={pattern} onChange={e => setPattern(e.target.value)}
                        placeholder="{date:%Y-%m-%d}_{stem}" className="text-xs font-mono" />
                      <div className="flex flex-wrap gap-1">
                        {TOKENS.map(tk => (
                          <button key={tk.token} onClick={() => setPattern(pattern + (pattern ? "" : "") + tk.token)}
                            className="text-[10px] px-1.5 py-0.5 rounded bg-muted hover:bg-primary/10 border font-mono">
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
            <CardHeader><CardTitle>{t("3. Options", "3. Optionen")}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <label className="flex items-center gap-2 text-xs cursor-pointer">
                <input type="checkbox" checked={recursive}
                  onChange={e => setRecursive(e.target.checked)} />
                {t("Include subdirectories", "Unterordner einbeziehen")}
              </label>
              <label className="flex items-center gap-2 text-xs cursor-pointer">
                <input type="checkbox" checked={includeHidden}
                  onChange={e => setIncludeHidden(e.target.checked)} />
                {t("Include hidden files", "Versteckte Dateien einbeziehen")}
              </label>
              <div>
                <label className="text-xs font-medium">{t("Date source", "Datumsquelle")}</label>
                <select value={dateSource} onChange={e => setDateSource(e.target.value as any)}
                  className="text-xs border rounded px-2 py-1 bg-background w-full mt-1">
                  <option value="auto">{t("Auto (smart detection)", "Auto (intelligente Erkennung)")}</option>
                  <option value="exif">{t("EXIF metadata only", "Nur EXIF-Metadaten")}</option>
                  <option value="filename">{t("Filename only", "Nur Dateiname")}</option>
                  <option value="mtime">{t("File modification date", "Dateiänderungsdatum")}</option>
                </select>
              </div>
            </CardContent>
          </Card>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <Button onClick={runPreview} disabled={loading} className="w-full" size="lg">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {t("Preview Rename", "Vorschau Umbenennung")}
          </Button>
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
        <main className="max-w-2xl mx-auto p-6 space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-2">
            <Card className="text-center p-3"><p className="text-xl font-bold text-green-600">{preview.planned_count.toLocaleString()}</p><p className="text-[10px] text-muted-foreground">{t("Planned", "Geplant")}</p></Card>
            <Card className="text-center p-3"><p className="text-xl font-bold text-amber-600">{preview.skipped_count.toLocaleString()}</p><p className="text-[10px] text-muted-foreground">{t("Skipped", "Überspr.")}</p></Card>
            <Card className="text-center p-3"><p className="text-xl font-bold text-red-600">{preview.conflict_count.toLocaleString()}</p><p className="text-[10px] text-muted-foreground">{t("Conflicts", "Konflikte")}</p></Card>
            <Card className="text-center p-3"><p className="text-xl font-bold text-blue-600">{preview.error_count.toLocaleString()}</p><p className="text-[10px] text-muted-foreground">{t("Errors", "Fehler")}</p></Card>
          </div>

          {/* File list preview (OLD NAME → NEW NAME) */}
          {preview.entries && preview.entries.length > 0 && (
            <Card>
              <CardHeader><CardTitle>{t("Files to rename", "Umzubenennende Dateien")} ({preview.entries.length.toLocaleString()})</CardTitle></CardHeader>
              <CardContent className="max-h-64 overflow-y-auto space-y-1">
                {preview.entries.slice(0, 20).map((e, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs py-1 border-b last:border-0">
                    <span className="font-mono truncate flex-1 text-muted-foreground">{e.source_path?.split(/[\\/]/).pop()}</span>
                    <span className="text-primary shrink-0">→</span>
                    <span className="font-mono truncate flex-1">{e.target_path?.split(/[\\/]/).pop() || "—"}</span>
                    <Badge variant={e.status === "planned" ? "default" : e.status === "skipped" ? "secondary" : "destructive"} className="text-[9px] shrink-0">{e.status}</Badge>
                  </div>
                ))}
                {preview.entries.length > 20 && (
                  <p className="text-[10px] text-muted-foreground text-center pt-1">
                    {t(`... and ${preview.entries.length - 20} more`, `... und ${preview.entries.length - 20} weitere`)}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {error && <p className="text-sm text-red-500">{error}</p>}

          <Button onClick={runApply} disabled={loading || preview.planned_count === 0} className="w-full" size="lg" variant="default">
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
        <main className="max-w-xl mx-auto p-6 space-y-6 text-center">
          {/* Success */}
          <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto">
            <Check className="h-10 w-10 text-green-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold">{t("Renaming complete!", "Umbenennung abgeschlossen!")}</h2>
            <p className="text-muted-foreground mt-1">
              {t(`${result.renamed_count} files renamed`, `${result.renamed_count} Dateien umbenannt`)}
            </p>
            {result.skipped_count > 0 && (
              <p className="text-sm text-muted-foreground mt-1">
                + {result.skipped_count} {t("skipped", "übersprungen")}
                {result.error_count > 0 ? `, ${result.error_count} ${t("errors", "Fehler")}` : ""}
              </p>
            )}
          </div>

          {/* Donation */}
          <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/10 border-amber-200">
            <CardContent className="p-4 space-y-3">
              <Heart className="h-6 w-6 text-red-500 mx-auto" fill="currentColor" />
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
            <Button onClick={startOver} variant="outline">
              <RotateCcw className="h-4 w-4 mr-1" /> {t("Rename more", "Weitere umbenennen")}
            </Button>
            <Button onClick={() => navigate("/library")} variant="default">
              {t("View Library", "Bibliothek ansehen")} <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </main>
      </>
    )
  }

  return null
}
