import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { convertFileSrc } from "@tauri-apps/api/core"
import {
  runtimeDiagnostics,
  settingsRead,
  historyList,
  organizePreview,
  organizeApply,
  libraryBrowsePaginated,
  type RuntimeDiagnostics,
  type HistoryListPayload,
  type HistoryRunEntry,
} from "@/lib/tauri-bridge"
import type { GuiSettings, OrganizePreviewResponse, OperationMode } from "@/types"
import { EmptyState } from "@/components/shared/EmptyState"
import { cn } from "@/lib/utils"
import { runPreflight } from "@/lib/preflight-guard"
import { Zap, Loader2, Copy, MoveRight, Clock, BarChart3 } from "lucide-react"

const QUICK_WORKFLOWS = [
  { id: "organize-date-library", label: "Organize Library", desc: "Sort photos into year/month/day folders", page: "/organize", icon: "📁" },
  { id: "duplicate-review-safe", label: "Find Duplicates", desc: "Scan for exact duplicate files", page: "/duplicates", icon: "🔍" },
  { id: "rename-capture-standard", label: "Standardize Names", desc: "Rename to date_stem format", page: "/organize", icon: "✏️" },
  { id: "trip-hardlink-collection", label: "Trip Collection", desc: "Build trip from date range", page: "/organize", icon: "✈️" },
  { id: "cleanup-family-library", label: "Cleanup Workflow", desc: "Full scan → organize → cleanup", page: "/organize", icon: "🧹" },
] as const

interface DashboardData {
  diag: RuntimeDiagnostics | null
  diagError: string | null
  settings: GuiSettings | null
  settingsError: string | null
  history: HistoryListPayload | null
  historyError: string | null
}

const getGreeting = (t: (en: string, de: string) => string) => {
  const hour = new Date().getHours()
  if (hour < 12) return t("Good morning!", "Guten Morgen!")
  if (hour < 18) return t("Good afternoon!", "Guten Tag!")
  return t("Good evening!", "Guten Abend!")
}

export default function DashboardPage() {
  const t = useT()
  const [data, setData] = useState<DashboardData>({
    diag: null,
    diagError: null,
    settings: null,
    settingsError: null,
    history: null,
    historyError: null,
  })
  const [loading, setLoading] = useState(false)
  const [organizing, setOrganizing] = useState(false)
  const [quickResult, setQuickResult] = useState<OrganizePreviewResponse | null>(null)
  const [quickMode, setQuickMode] = useState<OperationMode>("copy")
  const [preflight, setPreflight] = useState<{ ok: boolean; issues: string[] } | null>(null)
  const navigate = useNavigate()
  const [recentFiles, setRecentFiles] = useState<Array<{name: string; path: string; suffix: string; relative: string; modified: string}>>([])
  const [recentLoading, setRecentLoading] = useState(false)
  const [libStats, setLibStats] = useState<{total: number; other: number} | null>(null)

  const defaultSource = data.settings?.recent_paths?.profile_dir || localStorage.getItem("default_source_dir") || ""

  useEffect(() => {
    const src = defaultSource
    if (src) {
      runPreflight(src).then(setPreflight)
    } else {
      runtimeDiagnostics().then(d => {
        setPreflight({ ok: d.python_reachable, issues: d.python_reachable ? [] : [d.python_error ?? "Python not reachable"] })
      })
    }
  }, [defaultSource])

  useEffect(() => {
    const defaultSource = localStorage.getItem("default_source_dir") || localStorage.getItem("library_root")
    if (!defaultSource) return
    setRecentLoading(true)
    libraryBrowsePaginated({ root_dir: defaultSource, page: 0, page_size: 6 })
      .then(r => {
        const sorted = [...r.files].sort((a, b) => 
          new Date(b.modified || 0).getTime() - new Date(a.modified || 0).getTime()
        )
        setRecentFiles(sorted.slice(0, 6))
      })
      .catch(() => {})
      .finally(() => setRecentLoading(false))
  }, [])

  useEffect(() => {
    const defaultSource = localStorage.getItem("default_source_dir") || localStorage.getItem("library_root")
    if (!defaultSource) return
    libraryBrowsePaginated({ root_dir: defaultSource, page: 0, page_size: 1 })
      .then(r => {
        setLibStats({
          total: r.file_count,
          other: r.other_count || 0
        })
      })
      .catch(() => {})
  }, [])

  const handleQuickOrganize = async () => {
    if (!defaultSource) return
    setOrganizing(true)
    setQuickResult(null)
    try {
      const options = {
        source_dirs: [defaultSource],
        target_root: defaultSource,
        pattern: "{YYYY}/{MM}/{DD}_{stem}",
        recursive: true,
        include_hidden: false,
        follow_symlinks: false,
        operation_mode: quickMode,
        exiftool_path: null,
        include_associated_files: true,
        conflict_policy: "rename" as const,
        include_patterns: [],
        exclude_patterns: [],
        batch_size: 0,
      }
      const preview = await organizePreview(options)
      setQuickResult(preview)
    } catch (err) {
      setQuickResult(null)
    } finally {
      setOrganizing(false)
    }
  }

  const handleQuickApply = async () => {
    if (!defaultSource || !quickResult) return
    setOrganizing(true)
    try {
      await organizeApply(quickResult.options ?? {
        source_dirs: [defaultSource],
        target_root: defaultSource,
        pattern: "{YYYY}/{MM}/{DD}_{stem}",
        recursive: true,
        include_hidden: false,
        follow_symlinks: false,
        operation_mode: quickMode,
        exiftool_path: null,
        include_associated_files: true,
        conflict_policy: "rename",
        include_patterns: [],
        exclude_patterns: [],
        batch_size: 0,
      })
      setQuickResult(null)
    } catch {
      // ignore
    } finally {
      setOrganizing(false)
    }
  }

  const load = useCallback(async () => {
    const result: DashboardData = {
      diag: null,
      diagError: null,
      settings: null,
      settingsError: null,
      history: null,
      historyError: null,
    }

    setLoading(true)

    // Fetch all three sources independently
    const [diagRes, settingsRes, historyRes] = await Promise.allSettled([
      runtimeDiagnostics(),
      settingsRead(),
      historyList(),
    ])

    if (diagRes.status === "fulfilled") {
      result.diag = diagRes.value
    } else {
      result.diagError = String(diagRes.reason)
    }

    if (settingsRes.status === "fulfilled") {
      result.settings = settingsRes.value
    } else {
      result.settingsError = String(settingsRes.reason)
    }

    if (historyRes.status === "fulfilled") {
      result.history = historyRes.value
    } else {
      result.historyError = String(historyRes.reason)
    }

    setData(result)
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const pythonOk = data.diag?.python_reachable === true
  const latestRun: HistoryRunEntry | null =
    data.history && data.history.runs.length > 0 ? data.history.runs[0] : null
  const hasAnyError = data.diagError || data.settingsError || data.historyError

  const stats = useMemo(() => {
    if (!data.diag || !data.history) return null
    const runs = data.history.runs || []
    const applyRuns = runs.filter(r => r.mode === "apply")
    const previewRuns = runs.filter(r => r.mode === "preview")
    const successful = runs.filter(r => r.status === "success" || r.exit_code === 0)
    const byCommand: Record<string, number> = {}
    for (const r of runs) {
      const cmd = r.command || "unknown"
      byCommand[cmd] = (byCommand[cmd] || 0) + 1
    }
    const totalActions = runs.reduce((sum, r) => sum + (r.action_count || 0), 0)
    const totalRecommended = runs.reduce((sum, r) => sum + (r.recommended_action_count || 0), 0)
    return {
      totalRuns: runs.length,
      applyRuns: applyRuns.length,
      previewRuns: previewRuns.length,
      successRate: runs.length > 0 ? Math.round((successful.length / runs.length) * 100) : 100,
      byCommand,
      totalActions,
      totalRecommended,
      lastApply: applyRuns.length > 0 ? applyRuns[0] : null,
      lastPreview: previewRuns.length > 0 ? previewRuns[0] : null,
    }
  }, [data.diag, data.history])

  return (
    <>
      <PageHeader
        title={t("Dashboard", "Dashboard")}
        subtitle={getGreeting(t)}
      >
        <Button
          variant="outline"
          size="sm"
          onClick={load}
          disabled={loading}
        >
          {loading ? t("Refreshing...", "Aktualisiere...") : t("Refresh", "Aktualisieren")}
        </Button>
      </PageHeader>
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-4xl space-y-4">
          {/* Error summary */}
          {hasAnyError && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive space-y-1">
              {data.diagError && <p>Diagnostics: {data.diagError}</p>}
              {data.settingsError && <p>Settings: {data.settingsError}</p>}
              {data.historyError && <p>History: {data.historyError}</p>}
            </div>
          )}

          {/* Preflight status */}
          {preflight && !preflight.ok && preflight.issues.length > 0 && (
            <div className="rounded-lg border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-950 px-4 py-3 text-sm text-yellow-800 dark:text-yellow-200 space-y-1">
              {preflight.issues.map((issue, i) => (
                <p key={i}>⚠ {issue}</p>
              ))}
            </div>
          )}

          {/* Quick Organize Card */}
          <Card className="col-span-2 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950/20 dark:to-indigo-950/10">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-blue-500" />
                {t("Quick Organize", "Schnell-Organisieren")}
              </CardTitle>
              <CardDescription>
                {t("One-click organization of your default source directory",
                   "Ein-Klick-Organisation deines Standard-Quellverzeichnisses")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {defaultSource ? (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground truncate">
                    {t(`Source: ${defaultSource}`, `Quelle: ${defaultSource}`)}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant={quickMode === "copy" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setQuickMode("copy")}
                    >
                      <Copy className="h-3.5 w-3.5 mr-1" />
                      {t("Copy", "Kopieren")}
                    </Button>
                    <Button
                      variant={quickMode === "move" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setQuickMode("move")}
                    >
                      <MoveRight className="h-3.5 w-3.5 mr-1" />
                      {t("Move", "Verschieben")}
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleQuickOrganize} disabled={organizing}>
                      <Loader2 className={cn("h-4 w-4 mr-2", organizing && "animate-spin")} />
                      {organizing ? t("Organizing...", "Organisiere...") : t("Organize Now", "Jetzt organisieren")}
                    </Button>
                    {quickResult && (
                      <Button variant="outline" onClick={() => navigate("/organize")}>
                        {t("Review Details", "Details prüfen")}
                      </Button>
                    )}
                  </div>
                  {quickResult && (
                    <div className="rounded-lg border bg-background/50 p-3 space-y-1 text-sm">
                      <p>
                        <span className="font-medium">{quickResult.planned_count}</span>{" "}
                        {t("files planned", "Dateien geplant")}
                      </p>
                      <p className="text-muted-foreground">
                        {quickResult.conflict_count} {t("conflicts", "Konflikte")},{" "}
                        {quickResult.error_count} {t("errors", "Fehler")}
                      </p>
                      {quickResult.skipped_count > 0 && (
                        <p className="text-muted-foreground">
                          {quickResult.skipped_count} {t("skipped", "übersprungen")}
                        </p>
                      )}
                      <div className="flex gap-2 pt-2">
                        <Button size="sm" variant="default" onClick={handleQuickApply} disabled={organizing || quickResult.planned_count === 0}>
                          {organizing ? t("Applying...", "Wende an...") : t("Apply", "Anwenden")}
                        </Button>
                        <Button size="sm" variant="ghost" onClick={() => setQuickResult(null)}>
                          {t("Dismiss", "Verwerfen")}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted-foreground mb-3">
                    {t("Set a default source directory in Settings first.",
                       "Lege zuerst ein Standard-Quellverzeichnis in den Einstellungen fest.")}
                  </p>
                  <Button variant="outline" onClick={() => navigate("/settings")}>
                    {t("Open Settings", "Einstellungen öffnen")}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recently Added + Library Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  {t("Recently Added", "Kürzlich hinzugefügt")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {recentLoading ? (
                  <div className="space-y-2">
                    {[1,2,3].map(i => <Skeleton key={i} className="h-10 w-full" />)}
                  </div>
                ) : recentFiles.length > 0 ? (
                  <div className="space-y-1">
                    {recentFiles.map((f, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs py-1 hover:bg-muted/50 rounded px-1 cursor-pointer"
                        role="button" tabIndex={0}>
                        <img src={convertFileSrc(f.path)} className="h-8 w-8 rounded object-cover bg-muted" alt={f.name} />
                        <div className="flex-1 min-w-0">
                          <p className="truncate font-medium">{f.name}</p>
                          <p className="text-muted-foreground text-[10px]">{f.relative}</p>
                        </div>
                        <span className="text-[10px] text-muted-foreground shrink-0">
                          {new Date(f.modified).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    {t("No files found in default directory.", "Keine Dateien im Standardverzeichnis.")}
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  {t("Library Stats", "Bibliothek-Statistiken")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {libStats ? (
                  <div className="grid grid-cols-2 gap-3">
                    <div className="text-center p-2 rounded bg-muted/30">
                      <p className="text-2xl font-bold">{libStats.total.toLocaleString()}</p>
                      <p className="text-[10px] text-muted-foreground">{t("Total files", "Dateien gesamt")}</p>
                    </div>
                    <div className="text-center p-2 rounded bg-muted/30">
                      <p className="text-2xl font-bold">{libStats.other.toLocaleString()}</p>
                      <p className="text-[10px] text-muted-foreground">{t("Other files", "Andere Dateien")}</p>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    {t("Set a default directory to see stats.", "Standardverzeichnis festlegen für Statistiken.")}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
              <Card className="p-4">
                <p className="text-2xl font-bold">{stats.totalRuns}</p>
                <p className="text-xs text-muted-foreground">{t("Total runs", "Durchläufe gesamt")}</p>
              </Card>
              <Card className="p-4">
                <p className="text-2xl font-bold text-green-400">{stats.applyRuns}</p>
                <p className="text-xs text-muted-foreground">{t("Applied runs", "Angewendet")}</p>
              </Card>
              <Card className="p-4">
                <p className="text-2xl font-bold">{stats.successRate}%</p>
                <p className="text-xs text-muted-foreground">{t("Success rate", "Erfolgsquote")}</p>
              </Card>
              <Card className="p-4">
                <p className="text-2xl font-bold">{stats.totalActions}</p>
                <p className="text-xs text-muted-foreground">{t("Total actions", "Aktionen gesamt")}</p>
              </Card>
            </div>
          )}

          {stats && Object.keys(stats.byCommand).length > 1 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {Object.entries(stats.byCommand).map(([cmd, count]) => (
                <Badge key={cmd} variant="secondary" className="text-xs">
                  {cmd}: {count}
                </Badge>
              ))}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* System Status */}
            <Card>
              <CardHeader>
                <CardTitle>{t("System Status", "Systemstatus")}</CardTitle>
                <CardDescription>
                  {t("Python bridge health and environment.", "Python-Bridge-Status und Umgebung.")}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {loading && !data.diag ? (
                  <div className="flex justify-center py-4" aria-label={t("Loading diagnostics", "Diagnose wird geladen")}>
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  </div>
                ) : (
                  <>
                <StatusRow
                  label={t("Python bridge", "Python-Bridge")}
                  ok={pythonOk}
                  detail={
                    data.diag
                      ? data.diag.python_version?.split(" ")[0] ?? t("reachable", "erreichbar")
                      : data.diagError
                        ? t("unreachable", "nicht erreichbar")
                        : t("checking...", "Prüfe...")
                  }
                />
                <StatusRow
                  label={t("Settings file", "Einstellungsdatei")}
                  ok={data.diag?.settings_file_exists}
                  detail={
                    data.diag?.settings_file_exists
                      ? t("found", "gefunden")
                      : data.diag
                        ? t("not found", "nicht gefunden")
                        : "—"
                  }
                />
                <StatusRow
                  label={t("Project root", "Projektstamm")}
                  ok={!!data.diag?.project_root}
                  detail={data.diag?.project_root ? t("resolved", "aufgelöst") : "—"}
                />

                {data.diag && (
                  <div className="pt-2 border-t text-xs text-muted-foreground space-y-0.5">
                    <p className="truncate font-mono">
                      {data.diag.python_exe}
                    </p>
                    {data.diag.settings_path && (
                      <p className="truncate font-mono">
                        {data.diag.settings_path}
                      </p>
                    )}
                  </div>
                )}
                  </>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>{t("Recent Activity", "Letzte Aktivität")}</CardTitle>
                <CardDescription>
                  {t("Run history and operation summary.", "Verlauf und Zusammenfassung.")}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {data.history ? (
                  <>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold tabular-nums">
                        {data.history.run_count}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {t("total runs", "Durchläufe gesamt")}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-sm">
                      <Badge variant="secondary">
                        {data.history.valid_count} {t("valid", "gültig")}
                      </Badge>
                      {data.history.invalid_count > 0 && (
                        <Badge variant="destructive">
                          {data.history.invalid_count} {t("invalid", "ungültig")}
                        </Badge>
                      )}
                    </div>

                    {latestRun ? (
                      <button
                        onClick={() =>
                          navigate(`/history/${latestRun.run_id}`)
                        }
                        aria-label={`View run ${latestRun.run_id}`}
                        className="w-full rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
                      >
                        <span aria-hidden="true">
                          <p className="text-xs text-muted-foreground">
                            {t("Latest run", "Letzter Durchlauf")}
                          </p>
                          <p className="truncate font-mono text-sm font-medium">
                            {latestRun.run_id}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge
                              variant={
                                latestRun.mode === "apply"
                                  ? "default"
                                  : "secondary"
                              }
                              className="text-xs"
                            >
                              {latestRun.mode === "apply"
                                ? t("Applied", "Angewendet")
                                : latestRun.mode === "preview"
                                  ? t("Preview", "Vorschau")
                                  : "—"}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {latestRun.command ?? "—"}
                            </span>
                            {latestRun.created_at_utc && (
                              <span className="text-xs text-muted-foreground">
                                {latestRun.created_at_utc.slice(0, 10)}
                              </span>
                            )}
                          </div>
                          {latestRun && (
                            <div className="space-y-1 mt-2">
                              <div className="flex items-center gap-2">
                                <Badge variant={latestRun.mode === "apply" ? "default" : "secondary"} className="text-xs">
                                  {latestRun.mode}
                                </Badge>
                                <Badge variant="outline" className="text-xs">{latestRun.command}</Badge>
                                <span className="text-xs text-muted-foreground">{latestRun.run_id?.slice(0, 8)}</span>
                              </div>
                              {latestRun.review_candidate_count > 0 && (
                                <p className="text-xs text-yellow-400">
                                  {latestRun.review_candidate_count} {t("items need review", "Elemente benötigen Prüfung")}
                                </p>
                              )}
                            </div>
                          )}
                        </span>
                      </button>
                    ) : (
                      <EmptyState
                        title={t("No activity yet", "Noch keine Aktivität")}
                        description={t("Run your first organize, duplicates scan, or cleanup workflow to see results here.", "Führen Sie Ihren ersten Organisieren-, Duplikate-Scan oder Bereinigungs-Workflow aus, um hier Ergebnisse zu sehen.")}
                      />
                    )}
                  </>
                ) : (
                  <div className="text-sm text-muted-foreground">
                    {data.historyError
                      ? t("Could not load history.", "Verlauf konnte nicht geladen werden.")
                      : (
                        <span className="inline-flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                          {t("Loading...", "Lädt...")}
                        </span>
                      )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Settings at a glance */}
          {data.settings && (
            <Card>
              <CardHeader>
                <CardTitle>{t("Configuration", "Konfiguration")}</CardTitle>
                <CardDescription>
                  {t("Current settings at a glance.", "Aktuelle Einstellungen auf einen Blick.")}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">{t("Language", "Sprache")}</p>
                    <p className="font-medium">
                      {data.settings.language === "de" ? "Deutsch" : "English"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">{t("Theme", "Design")}</p>
                    <p className="font-medium">
                      {data.settings.theme === "modern-light"
                        ? t("Light", "Hell")
                        : t("Dark", "Dunkel")}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">{t("Start page", "Startseite")}</p>
                    <p className="font-medium capitalize">
                      {data.settings.start_page_id}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Quick navigation */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <QuickNavCard
              label={t("Organize", "Organisieren")}
              desc={t("Preview folder organization.", "Vorschau der Ordnerorganisation.")}
              onClick={() => navigate("/organize")}
            />
            <QuickNavCard
              label={t("Exact duplicates", "Exakte Duplikate")}
              desc={t("Find byte-identical files.", "Finde byte-identische Dateien.")}
              onClick={() => navigate("/duplicates")}
            />
            <QuickNavCard
              label={t("Similar images", "Ähnliche Bilder")}
              desc={t("Find visually similar images.", "Finde visuell ähnliche Bilder.")}
              onClick={() => navigate("/duplicates")}
            />
            <QuickNavCard
              label={t("Review", "Prüfung")}
              desc={t("Review candidates and record decisions.", "Kandidaten prüfen und Entscheidungen speichern.")}
              onClick={() => navigate("/review")}
            />
            <QuickNavCard
              label={t("History", "Verlauf")}
              desc={t("Browse past runs.", "Vergangene Durchläufe durchsuchen.")}
              onClick={() => navigate("/history")}
            />
            <QuickNavCard
              label={t("Settings", "Einstellungen")}
              desc={t("Language, theme, diagnostics.", "Sprache, Design, Diagnose.")}
              onClick={() => navigate("/settings")}
            />
          </div>

          {/* Quick Workflows */}
          <div className="mt-6">
            <h3 className="text-sm font-medium mb-3">{t("Quick Workflows", "Schnell-Workflows")}</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {QUICK_WORKFLOWS.map((wf) => (
                <Card
                  key={wf.id}
                  className="p-4 cursor-pointer hover:border-primary/50 transition-colors"
                  role="button"
                  tabIndex={0}
                  onClick={() => navigate(wf.page)}
                  onKeyDown={(e) => e.key === 'Enter' && navigate(wf.page)}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-xl">{wf.icon}</span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{t(wf.label, wf.label)}</p>
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{t(wf.desc, wf.desc)}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </main>
    </>
  )
}

function StatusRow({
  label,
  ok,
  detail,
}: {
  label: string
  ok?: boolean
  detail?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex size-2 shrink-0 rounded-full ${
          ok ? "bg-green-500" : "bg-destructive"
        }`}
      />
      <span className="text-sm font-medium">{label}</span>
      <span className="text-xs text-muted-foreground truncate">
        {detail ?? "—"}
      </span>
    </div>
  )
}

function QuickNavCard({
  label,
  desc,
  onClick,
  disabled,
}: {
  label: string
  desc: string
  onClick: () => void
  disabled?: boolean
}) {
  const t = useT()
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={`Navigate to ${label}`}
      className={`rounded-lg border p-3 text-left transition-colors ${
        disabled
          ? "opacity-50 cursor-not-allowed"
          : "hover:bg-muted/50"
      }`}
    >
      <p className="text-sm font-medium">
        {label}
        {disabled && (
          <span className="ml-1.5 text-[10px] text-muted-foreground font-normal">
            {t("coming soon", "demnächst")}
          </span>
        )}
      </p>
      <p className="text-xs text-muted-foreground">{desc}</p>
    </button>
  )
}
