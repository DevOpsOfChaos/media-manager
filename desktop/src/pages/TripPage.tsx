import { useState, useCallback, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { tripPreview, tripApply, libraryBrowse, type TripOptions, type TripPreviewResponse, type TripApplyResponse } from "@/lib/tauri-bridge"
import { useProgress } from "@/lib/progress-context"
import { convertFileSrc } from "@tauri-apps/api/core"
import { EmptyState } from "@/components/shared/EmptyState"
import { PageHeader } from "@/components/layout/PageHeader"
import { StepIndicator } from "@/components/shared/StepIndicator"
import { SuccessState } from "@/components/shared/SuccessState"
import { ErrorBanner } from "@/components/shared/ErrorBanner"
import { userFriendlyError, type FriendlyError } from "@/lib/error-utils"
import { useFirstRunHint } from "@/lib/use-first-run-hint"
import { loadFavorite, saveFavorite, hasFavorite } from "@/lib/favorites-store"
import { Plus, FolderOpen, Loader2, ImageOff, ChevronRight, Star, Map as MapIcon, Play, ChevronLeft, Check, X } from "lucide-react"

const STEPS = ["settings", "preview", "execute"] as const
type WizardStep = typeof STEPS[number]

interface TripEntry {
  name: string
  path: string
  fileCount: number
  thumbnail: string | null
}

function TripDetailView({ trip, onBack }: { trip: TripEntry; onBack: () => void }) {
  const t = useT()
  const [files, setFiles] = useState<Array<{path:string;name:string;suffix:string;size:number}>>([])
  const [loadingFiles, setLoadingFiles] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoadingFiles(true)
    libraryBrowse({ root_dir: trip.path }).then(r => {
      if (!cancelled) { setFiles(r.files); setLoadingFiles(false) }
    }).catch(() => { if (!cancelled) setLoadingFiles(false) })
    return () => { cancelled = true }
  }, [trip.path])

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={onBack}>{t("← Back", "← Zurück")}</Button>
        <h1 className="text-xl font-bold">{trip.name}</h1>
        <Badge variant="secondary">{trip.fileCount} {t("files", "Dateien")}</Badge>
      </div>
      {trip.thumbnail && (
        <img src={convertFileSrc(trip.thumbnail) || ""} alt={trip.name} className="w-full max-h-48 object-cover rounded-lg" />
      )}
      {loadingFiles ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
          {files.slice(0, 200).map((f, i) => (
            <div key={i} className="aspect-square bg-muted rounded overflow-hidden">
              {[".jpg",".jpeg",".png"].includes(f.suffix) ? (
                <img src={convertFileSrc(f.path) || ""} alt={f.name} className="w-full h-full object-cover" loading="lazy" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground/30"><FolderOpen className="w-8 h-8" /></div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function TripPage() {
  const t = useT()
  const { startProgress, updateProgress, finishProgress } = useProgress()

  const [tripsRoot, setTripsRoot] = useState(() => localStorage.getItem("trips_root") || localStorage.getItem("default_source_dir") || "")
  const [trips, setTrips] = useState<TripEntry[]>([])
  const [loadingTrips, setLoadingTrips] = useState(false)

  const [wizardStep, setWizardStep] = useState<WizardStep | null>(null)
  const [sourceDirs, setSourceDirs] = useState<string[]>([""])
  const [targetRoot, setTargetRoot] = useState("")
  const [label, setLabel] = useState("")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [mode, setMode] = useState<"hardlink" | "copy">("hardlink")

  const [preview, setPreview] = useState<TripPreviewResponse | null>(null)
  const [result, setResult] = useState<TripApplyResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<FriendlyError | null>(null)

  const [isFavorite, setIsFavorite] = useState(() => hasFavorite("trip"))
  const [showHint, dismissHint] = useFirstRunHint("trip")
  const [selectedTrip, setSelectedTrip] = useState<TripEntry | null>(null)

  useEffect(() => {
    const fav = loadFavorite("trip")
    if (fav && !tripsRoot) {
      if (fav.tripsRoot) setTripsRoot(fav.tripsRoot)
    }
  }, [])

  const loadTrips = useCallback(async () => {
    if (!tripsRoot) return
    setLoadingTrips(true)
    try {
      const result = await libraryBrowse({ root_dir: tripsRoot, max_depth: 1 })
      const tripMap = new Map<string, { files: number; thumb: string | null }>()
      for (const f of result.files || []) {
        const parts = f.relative.replace(/\\/g, "/").split("/")
        const tripName = parts[0] || "unknown"
        if (!tripMap.has(tripName)) tripMap.set(tripName, { files: 0, thumb: null })
        const tr = tripMap.get(tripName)!
        tr.files++
        if (!tr.thumb && [".jpg", ".jpeg", ".png"].includes(f.suffix)) tr.thumb = f.path
      }
      const entries: TripEntry[] = []
      for (const [name, info] of tripMap) {
        entries.push({ name, path: `${tripsRoot}/${name}`, fileCount: info.files, thumbnail: info.thumb })
      }
      entries.sort((a, b) => b.name.localeCompare(a.name))
      setTrips(entries)
    } catch { /* ignore */ }
    finally { setLoadingTrips(false) }
  }, [tripsRoot])

  useEffect(() => { if (tripsRoot) loadTrips() }, [tripsRoot])

  const addSourceDir = () => setSourceDirs(prev => [...prev, ""])
  const removeSourceDir = (i: number) => setSourceDirs(prev => prev.filter((_, idx) => idx !== i))
  const setSourceDir = (i: number, val: string) => setSourceDirs(prev => prev.map((d, idx) => idx === i ? val : d))

  const computedTotalSizeGb = (): string => {
    if (!preview) return "—"
    const totalBytes = preview.entries.reduce((sum, e) => sum + (e.size_bytes || 0), 0)
    return (totalBytes / (1024 * 1024 * 1024)).toFixed(1)
  }

  const runPreview = async () => {
    const cleanDirs = sourceDirs.filter(Boolean)
    if (cleanDirs.length === 0) {
      setError({ message: t("At least one source directory required", "Mindestens ein Quellverzeichnis erforderlich"), suggestion: null })
      return
    }
    if (!targetRoot) {
      setError({ message: t("Target root required", "Zielverzeichnis erforderlich"), suggestion: null })
      return
    }
    if (!label) {
      setError({ message: t("Trip label required", "Reisebezeichnung erforderlich"), suggestion: null })
      return
    }
    setLoading(true); setError(null); setPreview(null)
    startProgress(t("Building trip preview...", "Erstelle Reise-Vorschau..."), 100)
    try {
      const options: TripOptions = {
        source_dirs: cleanDirs,
        target_root: targetRoot,
        label,
        start_date: dateFrom,
        end_date: dateTo,
        use_hardlinks: mode === "hardlink",
      }
      const r = await tripPreview(options)
      updateProgress(100)
      setPreview(r)
      setWizardStep("preview")
    } catch (e) {
      setError(userFriendlyError(e))
    } finally {
      setTimeout(() => finishProgress(), 500)
      setLoading(false)
    }
  }

  const runApply = async () => {
    if (!preview || preview.planned_count === 0) return
    const cleanDirs = sourceDirs.filter(Boolean)
    setLoading(true); setError(null)
    startProgress(t("Creating trip...", "Reise wird erstellt..."), preview.planned_count)
    try {
      const options: TripOptions = {
        source_dirs: cleanDirs,
        target_root: targetRoot,
        label,
        start_date: dateFrom,
        end_date: dateTo,
        use_hardlinks: mode === "hardlink",
      }
      const r = await tripApply(options)
      updateProgress(preview.planned_count)
      setResult(r)
      setWizardStep("execute")
      loadTrips()
      localStorage.setItem("trips_root", targetRoot)
    } catch (e) {
      setError(userFriendlyError(e))
    } finally {
      setTimeout(() => finishProgress(), 500)
      setLoading(false)
    }
  }

  const startOver = () => {
    setWizardStep("settings")
    setPreview(null)
    setResult(null)
    setError(null)
  }

  const exitWizard = () => {
    setWizardStep(null)
    setPreview(null)
    setResult(null)
    setError(null)
    setSourceDirs([""])
    setLabel("")
    setDateFrom("")
    setDateTo("")
    setMode("hardlink")
  }

  if (selectedTrip) {
    return <TripDetailView trip={selectedTrip} onBack={() => setSelectedTrip(null)} />
  }

  if (wizardStep) {
    const dateRangeStr = dateFrom && dateTo ? `${dateFrom} — ${dateTo}` : "—"

    if (wizardStep === "settings") {
      return (
        <div className="max-w-5xl mx-auto p-6 space-y-6">
          <StepIndicator steps={[
            { id: 'settings', label: t('Settings', 'Einstellungen'), active: true },
            { id: 'preview', label: t('Preview', 'Vorschau') },
            { id: 'execute', label: t('Execute', 'Ausführen') },
          ]} />

          <Card>
            <CardHeader><CardTitle>{t("1. Source directories", "1. Quellverzeichnisse")}</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              {sourceDirs.map((dir, i) => (
                <div key={i} className="flex gap-2">
                  <Input value={dir} onChange={e => setSourceDir(i, e.target.value)}
                    placeholder={t("G:\\Photos", "G:\\Fotos")} className="text-sm" />
                  {sourceDirs.length > 1 && (
                    <Button variant="ghost" size="icon" onClick={() => removeSourceDir(i)} aria-label={t("Remove", "Entfernen")}>
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              <Button variant="outline" size="sm" onClick={addSourceDir}>
                + {t("Add source", "Quelle hinzufügen")}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>{t("2. Target & Label", "2. Ziel & Bezeichnung")}</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <Input value={targetRoot} onChange={e => setTargetRoot(e.target.value)}
                placeholder="G:\\Trips" className="text-sm" />
              <Input value={label} onChange={e => setLabel(e.target.value)}
                placeholder="Italy 2024" className="text-sm" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>{t("3. Date Range & Mode", "3. Zeitraum & Modus")}</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <Input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="text-sm" />
                <Input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} className="text-sm" />
              </div>
              <div className="flex gap-4 text-sm">
                <label className="flex items-center gap-2">
                  <input type="radio" checked={mode === 'hardlink'} onChange={() => setMode('hardlink')} />
                  {t("Hardlinks", "Hardlinks")}
                </label>
                <label className="flex items-center gap-2">
                  <input type="radio" checked={mode === 'copy'} onChange={() => setMode('copy')} />
                  {t("Copy", "Kopieren")}
                </label>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <Button variant="outline" onClick={exitWizard}>
              <ChevronLeft className="h-4 w-4 mr-1" /> {t("Back to list", "Zurück zur Liste")}
            </Button>
            <Button onClick={runPreview} className="flex-1" size="lg" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Play className="h-4 w-4 mr-2" />}
              {t("Preview", "Vorschau")}
            </Button>
          </div>
        </div>
      )
    }

    if (wizardStep === "preview" && preview) {
      return (
        <div className="max-w-5xl mx-auto p-6 space-y-6">
          <PageHeader title={t("Trip Preview", "Reise-Vorschau")}>
            <Button variant="outline" size="sm" onClick={() => setWizardStep("settings")}>
              <ChevronLeft className="h-4 w-4 mr-1" /> {t("Back", "Zurück")}
            </Button>
          </PageHeader>

          <StepIndicator steps={[
            { id: 'settings', label: t('Settings', 'Einstellungen'), done: true },
            { id: 'preview', label: t('Preview', 'Vorschau'), active: true },
            { id: 'execute', label: t('Execute', 'Ausführen') },
          ]} />

          <div className="grid grid-cols-3 gap-2">
            <Card className="text-center p-3">
              <p className="text-xl font-bold text-green-600">{preview.planned_count.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">{t("Files", "Dateien")}</p>
            </Card>
            <Card className="text-center p-3">
              <p className="text-xl font-bold">{computedTotalSizeGb()}</p>
              <p className="text-xs text-muted-foreground">GB</p>
            </Card>
            <Card className="text-center p-3">
              <p className="text-xl font-bold">{dateRangeStr}</p>
              <p className="text-xs text-muted-foreground">{t("Period", "Zeitraum")}</p>
            </Card>
          </div>

          {error && <ErrorBanner message={error.message} suggestion={error.suggestion} />}

          <Button onClick={runApply} disabled={loading || preview.planned_count === 0} className="w-full" size="lg">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Check className="h-4 w-4 mr-2" />}
            {t("Create Trip", "Reise erstellen")}
          </Button>
        </div>
      )
    }

    if (wizardStep === "execute" && result) {
      return (
        <div className="max-w-5xl mx-auto p-6 space-y-6">
          <PageHeader title={t("Complete!", "Fertig!")} />
          <StepIndicator steps={[
            { id: 'settings', label: t('Settings', 'Einstellungen'), done: true },
            { id: 'preview', label: t('Preview', 'Vorschau'), done: true },
            { id: 'execute', label: t('Execute', 'Ausführen'), active: true },
          ]} />
          <SuccessState
            message={t("Trip created!", "Reise erstellt!")}
            action={
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  {result.linked_count > 0 && `${result.linked_count} ${t("linked", "verknüpft")}`}
                  {result.linked_count > 0 && result.copied_count > 0 && ", "}
                  {result.copied_count > 0 && `${result.copied_count} ${t("copied", "kopiert")}`}
                </p>
                <div className="flex gap-2 justify-center">
                  <Button onClick={startOver} variant="outline" size="sm">
                    {t("Create another", "Weitere erstellen")}
                  </Button>
                  <Button onClick={exitWizard} variant="default" size="sm">
                    <ChevronRight className="h-4 w-4 ml-1" /> {t("View trips", "Reisen ansehen")}
                  </Button>
                </div>
              </div>
            }
          />
        </div>
      )
    }
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">

      <PageHeader
        title={t("Trips", "Reisen")}
        subtitle={t("Your trip collections.", "Ihre Reisesammlungen.")}
      >
        <Button onClick={() => {
          setWizardStep("settings")
          setPreview(null)
          setResult(null)
          setError(null)
          setSourceDirs([""])
          setTargetRoot(tripsRoot)
          setLabel("")
          setDateFrom("")
          setDateTo("")
          setMode("hardlink")
        }} size="sm">
          <Plus className="w-4 h-4 mr-1" /> {t("New Trip", "Neue Reise")}
        </Button>
      </PageHeader>
      {showHint && (
        <div data-hint className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800/30 rounded-lg p-3 text-sm">
          <p>{t("Create trip collections from your organized photos using date ranges. Each trip gets its own folder with hardlinks.", "Erstelle Reisesammlungen aus deinen organisierten Fotos mit Datumsbereichen. Jede Reise bekommt einen eigenen Ordner mit Hardlinks.")}</p>
          <button onClick={dismissHint}
            className="text-xs text-blue-500 dark:text-blue-400 mt-1 hover:underline">{t("Got it", "Verstanden")}</button>
        </div>
      )}

      <div className="flex items-center gap-2">
        <Input value={tripsRoot} onChange={e => { setTripsRoot(e.target.value); localStorage.setItem("trips_root", e.target.value) }} placeholder={t("Trips root directory (e.g. C:\\Trips)", "Reise-Stammverzeichnis (z.B. C:\\Reisen)")} className="text-xs w-64" />
        <Button onClick={loadTrips} variant="outline" size="sm" disabled={!tripsRoot || loadingTrips}>
          {loadingTrips ? <Loader2 className="w-4 h-4 animate-spin" /> : t("Refresh", "Aktualisieren")}
        </Button>
        {trips.length > 0 && <Badge variant="secondary" className="ml-auto">{trips.length} {t("trips", "Reisen")}</Badge>}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              saveFavorite("trip", { tripsRoot })
              setIsFavorite(true)
            }}
            className="text-xs"
          >
            <Star className={`h-3 w-3 mr-1 ${isFavorite ? "fill-yellow-500 text-yellow-500 dark:fill-yellow-400 dark:text-yellow-400" : ""}`} />
            {isFavorite ? t("Favorite saved", "Favorit gespeichert") : t("Save as favorite", "Als Favorit speichern")}
          </Button>
      </div>

      {trips.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {trips.map(trip => (
            <Card key={trip.name} className="overflow-hidden cursor-pointer hover:border-primary/50 transition-colors" role="button" tabIndex={0} onClick={() => setSelectedTrip(trip)} onKeyDown={(e) => e.key === 'Enter' && setSelectedTrip(trip)}>
              <div className="aspect-video bg-muted relative overflow-hidden">
                {trip.thumbnail ? (
                  <img src={convertFileSrc(trip.thumbnail) || ""} alt={trip.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center"><ImageOff className="w-10 h-10 text-muted-foreground/30" /></div>
                )}
              </div>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{trip.name}</p>
                    <p className="text-xs text-muted-foreground">{trip.fileCount} {t("files", "Dateien")}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : !loadingTrips ? (
        <EmptyState icon={MapIcon} title={t("No trips yet", "Noch keine Reisen")} description={tripsRoot ? t("Click 'New Trip' to create your first trip collection.", "Klicken Sie 'Neue Reise', um Ihre erste Reisesammlung zu erstellen.") : t("Set your trips root directory above, then click Refresh.", "Legen Sie oben Ihr Reise-Stammverzeichnis fest und klicken Sie Aktualisieren.")} />
      ) : null}
    </div>
  )
}
