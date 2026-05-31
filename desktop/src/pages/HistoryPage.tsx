import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { userFriendlyError, type FriendlyError } from "@/lib/error-utils"
import { toast } from "@/lib/toast"
import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  historyList,
  undoApply,
  type HistoryListPayload,
  type HistoryRunEntry,
} from "@/lib/tauri-bridge"
import { EmptyState } from "@/components/shared/EmptyState"
import { Clock, SearchX, RotateCcw, BarChart3 } from "lucide-react"


export default function HistoryPage() {
  const t = useT()
  const [data, setData] = useState<HistoryListPayload | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<FriendlyError | null>(null)
  const [filter, setFilter] = useState("")
  const navigate = useNavigate()
  const [filterCommand, setFilterCommand] = useState<string>("all")
  const [filterMode, setFilterMode] = useState<string>("all")
  const [viewMode, setViewMode] = useState<"list" | "timeline">("list")
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedRuns, setSelectedRuns] = useState<Set<string>>(new Set())
  const [bulkUndoing, setBulkUndoing] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await historyList()
      setData(result)
    } catch (err) {
      setError(userFriendlyError(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const handleBulkUndo = useCallback(async () => {
    if (selectedRuns.size === 0) return
    setBulkUndoing(true)
    try {
      for (const runId of selectedRuns) {
        await undoApply(runId)
      }
      toast("success", t(`Undone ${selectedRuns.size} operations`, `${selectedRuns.size} Operationen rückgängig`))
      setSelectedRuns(new Set())
      await load()
    } catch (err) {
      toast("error", t("Bulk undo failed", "Massen-Rückgängig fehlgeschlagen"))
    } finally {
      setBulkUndoing(false)
    }
  }, [selectedRuns, t, load])

  const toggleSelectRun = useCallback((runId: string) => {
    setSelectedRuns(prev => {
      const next = new Set(prev)
      if (next.has(runId)) {
        next.delete(runId)
      } else {
        next.add(runId)
      }
      return next
    })
  }, [])

  const availableCommands = useMemo(() => {
    if (!data?.runs) return []
    const cmds = new Set(data.runs.map(r => r.command).filter(Boolean))
    return Array.from(cmds).sort()
  }, [data])

  const stats = useMemo(() => {
    if (!data?.runs) return null
    return {
      total: data.runs.length,
      valid: data.runs.filter(r => r.valid).length,
      invalid: data.runs.filter(r => !r.valid).length,
      previews: data.runs.filter(r => r.mode === "preview").length,
      applies: data.runs.filter(r => r.mode === "apply").length,
    }
  }, [data])

  const filteredRuns = useMemo(() => {
    if (!data) return []
    let runs = data.runs
    const q = filter.trim().toLowerCase()
    if (q) {
      runs = runs.filter(
        (r) =>
          r.run_id.toLowerCase().includes(q) ||
          (r.command ?? "").toLowerCase().includes(q) ||
          (r.mode ?? "").toLowerCase().includes(q) ||
          (r.status ?? "").toLowerCase().includes(q),
      )
    }
    const sq = searchQuery.trim().toLowerCase()
    if (sq) {
      runs = runs.filter(r =>
        JSON.stringify(r).toLowerCase().includes(sq)
      )
    }
    return runs.filter(r => {
      if (filterCommand !== "all" && r.command !== filterCommand) return false
      if (filterMode !== "all" && r.mode !== filterMode) return false
      return true
    })
  }, [data, filter, searchQuery, filterCommand, filterMode])

  return (
    <>
      <PageHeader title={t("History", "Verlauf")}>
        <Button
          variant="outline"
          size="sm"
          onClick={load}
          disabled={loading}
        >
          {loading ? (
            <span className="inline-flex items-center gap-1">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
              {t("Loading...", "Lädt...")}
            </span>
          ) : t("Refresh", "Aktualisieren")}
        </Button>
      </PageHeader>
      <main className="flex flex-1 gap-4 p-6">
        <div className="flex-1 max-w-5xl space-y-4">

          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive space-y-2">
              <p>{error.message}</p>
              <Button variant="outline" size="sm" onClick={load}>
                {t("Retry", "Wiederholen")}
              </Button>
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>{t("Run History", "Durchlauf-Verlauf")}</CardTitle>
              <CardDescription>
                {t("Browse past runs and inspect results.", "Vergangene Durchläufe durchsuchen und Ergebnisse prüfen.")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {loading && !data ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  <span className="ml-3 text-sm text-muted-foreground">{t("Loading history...", "Lade Verlauf...")}</span>
                </div>
              ) : null}

              {data && data.runs.length === 0 && (
                <EmptyState
                  icon={Clock}
                  title={t("No runs found", "Keine Durchläufe gefunden")}
                  description={t("Run an organize, rename, or duplicates command first. Apply-mode runs will appear here with undo support.", "Führen Sie zuerst einen Organisieren-, Umbenennen- oder Duplikate-Befehl aus. Angewendete Durchläufe erscheinen hier mit Rückgängig-Option.")}
                />
              )}

              {data && data.runs.length > 0 && (
                <>
                  {stats && (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                      <StatBadge icon={BarChart3} label={t("Total", "Gesamt")} value={stats.total} variant="default" />
                      <StatBadge label={t("Valid", "Gültig")} value={stats.valid} variant="success" />
                      <StatBadge label={t("Invalid", "Ungültig")} value={stats.invalid} variant={stats.invalid > 0 ? "destructive" : "default"} />
                      <StatBadge label={t("Previews", "Vorschauen")} value={stats.previews} variant="secondary" />
                      <StatBadge label={t("Applied", "Angewendet")} value={stats.applies} variant="default" />
                      <StatBadge label={t("Filtered", "Gefiltert")} value={filteredRuns.length} variant="outline" />
                    </div>
                  )}

                  <Input
                    type="text"
                    placeholder={t("Filter by run ID, command, mode, or status...", "Nach Durchlauf-ID, Befehl, Modus oder Status filtern...")}
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="h-8 text-sm"
                  />

                  <Input
                    type="text"
                    placeholder={t("Deep search (JSON)...", "Tiefensuche (JSON)...")}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="h-8 text-sm"
                  />

        <div className="flex flex-wrap items-center gap-2 mb-4">
          <select
            value={filterCommand}
            onChange={(e) => setFilterCommand(e.target.value)}
            className="text-xs rounded-md border border-border bg-background px-2 py-1.5 text-foreground"
            aria-label={t("Filter by command", "Nach Befehl filtern")}
          >
            <option value="all">{t("All commands", "Alle Befehle")}</option>
            {availableCommands.map(cmd => (
              <option key={cmd} value={cmd || ""}>{cmd}</option>
            ))}
          </select>
          <select
            value={filterMode}
            onChange={(e) => setFilterMode(e.target.value)}
            className="text-xs rounded-md border border-border bg-background px-2 py-1.5 text-foreground"
            aria-label={t("Filter by mode", "Nach Modus filtern")}
          >
            <option value="all">{t("All modes", "Alle Modi")}</option>
            <option value="apply">{t("Apply", "Anwenden")}</option>
            <option value="preview">{t("Preview", "Vorschau")}</option>
          </select>
          <div className="flex items-center gap-1 border rounded p-0.5">
            <button onClick={() => setViewMode("list")}
              className={`text-xs px-1.5 py-0.5 rounded ${viewMode === "list" ? "bg-primary text-primary-foreground" : "text-muted-foreground"}`}>
              {t("List", "Liste")}
            </button>
            <button onClick={() => setViewMode("timeline")}
              className={`text-xs px-1.5 py-0.5 rounded ${viewMode === "timeline" ? "bg-primary text-primary-foreground" : "text-muted-foreground"}`}>
              {t("Timeline", "Zeitleiste")}
            </button>
          </div>
          {selectedRuns.size > 0 && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleBulkUndo}
              disabled={bulkUndoing}
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1" />
              {bulkUndoing
                ? t("Undoing...", "Rückgängig...")
                : t(`Undo selected (${selectedRuns.size})`, `Auswahl rückgängig (${selectedRuns.size})`)}
            </Button>
          )}
          <span className="text-xs text-muted-foreground ml-auto">
            {filteredRuns.length} {t("of", "von")} {data?.runs?.length || 0} {t("runs", "Durchläufen")}
          </span>
        </div>

                  {filteredRuns.length === 0 ? (
                    <EmptyState
                      icon={SearchX}
                      title={t("No matching runs", "Keine passenden Durchläufe")}
                      description={t("No runs match the current filters. Try a different command or mode.", "Keine Durchläufe entsprechen den aktuellen Filtern. Versuchen Sie einen anderen Befehl oder Modus.")}
                    />
                  ) : viewMode === "timeline" ? (
                    <div className="relative pl-8 border-l-2 border-muted space-y-6">
                      {filteredRuns.map((run) => (
                        <div key={run.run_id} className="relative">
                          <div className={`absolute -left-[25px] w-3 h-3 rounded-full border-2 border-background ${
                            run.valid ? (run.mode === "apply" ? "bg-green-500 dark:bg-green-600" : "bg-blue-500 dark:bg-blue-400") : "bg-red-500 dark:bg-red-600"
                          }`} />
                          <Card className="cursor-pointer hover:border-primary/30 transition-colors"
                            onClick={() => navigate(`/history/${run.run_id}`)}
                            role="button" tabIndex={0}
                            onKeyDown={e => e.key === "Enter" && navigate(`/history/${run.run_id}`)}>
                            <CardContent className="p-3">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="text-sm font-medium">{run.command || t("Unknown", "Unbekannt")}</p>
                                  <p className="text-xs text-muted-foreground">
                                    {run.mode === "apply" ? t("Applied", "Angewendet") : t("Preview", "Vorschau")}
                                    {run.action_count > 0 && ` · ${run.action_count} ${t("actions", "Aktionen")}`}
                                    {run.review_candidate_count > 0 && ` · ${run.review_candidate_count} ${t("to review", "zu prüfen")}`}
                                  </p>
                                </div>
                                <div className="text-right">
                                  <p className="text-xs text-muted-foreground">
                                    {run.created_at_utc ? new Date(run.created_at_utc).toLocaleDateString() : "—"}
                                  </p>
                                  <Badge className={`text-xs ${run.valid ? "bg-green-500/10 text-green-500 dark:bg-green-500/15 dark:text-green-400" : "bg-red-500/10 text-red-500 dark:bg-red-500/15 dark:text-red-400"}`}>
                                    {run.valid ? t("Valid", "Gültig") : t("Invalid", "Ungültig")}
                                  </Badge>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {filteredRuns.map((run) => (
                        <RunRow
                          key={run.run_id}
                          run={run}
                          onClick={() => navigate(`/history/${run.run_id}`)}
                          selected={selectedRuns.has(run.run_id)}
                          onToggleSelect={() => toggleSelectRun(run.run_id)}
                        />
                      ))}
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  )
}

function RunRow({
  run,
  onClick,
  selected,
  onToggleSelect,
}: {
  run: HistoryRunEntry
  onClick: () => void
  selected?: boolean
  onToggleSelect?: () => void
}) {
  const t = useT()
  const modeLabel = run.mode === "apply" ? t("Applied", "Angewendet") : run.mode === "preview" ? t("Preview", "Vorschau") : "—"
  const modeVariant = run.mode === "apply" ? "default" : "secondary" as const

  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
    >
      <input
        type="checkbox"
        checked={selected ?? false}
        onChange={(e) => {
          e.stopPropagation()
          onToggleSelect?.()
        }}
        onClick={(e) => e.stopPropagation()}
        className="w-4 h-4 shrink-0 rounded border-border cursor-pointer"
        aria-label={t("Select run", "Durchlauf auswählen")}
      />
      <span
        className={`inline-flex size-2 shrink-0 rounded-full ${
          run.valid ? (run.exit_code === 0 ? "bg-green-500 dark:bg-green-600" : "bg-yellow-500 dark:bg-yellow-600") : "bg-destructive"
        }`}
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="truncate font-mono text-sm font-medium">
            {run.run_id}
          </span>
          <Badge variant={modeVariant} className="text-xs">
            {modeLabel}
          </Badge>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>{run.command ?? t("unknown", "unbekannt")}</span>
          {run.status && <span><span aria-hidden="true">· </span>{run.status}</span>}
          {run.created_at_utc && <span><span aria-hidden="true">· </span>{run.created_at_utc.slice(0, 10)}</span>}
        </div>
      </div>
      <div className="shrink-0 text-xs text-muted-foreground">
        {run.exit_code !== null && run.exit_code !== undefined
          ? `exit ${run.exit_code}`
          : "—"}
      </div>
    </button>
  )
}

function StatBadge({
  icon: Icon,
  label,
  value,
  variant,
}: {
  icon?: React.ComponentType<{ className?: string }>
  label: string
  value: number
  variant?: "default" | "secondary" | "destructive" | "outline" | "success"
}) {
  const variantClass = {
    default: "bg-primary/10 text-primary border-primary/20",
    secondary: "bg-muted text-muted-foreground border-border",
    destructive: "bg-destructive/10 text-destructive border-destructive/20",
    outline: "bg-background text-muted-foreground border-border",
    success: "bg-green-500/10 text-green-500 dark:bg-green-500/15 dark:text-green-400 border-green-500/20",
  }[variant ?? "default"]

  return (
    <div className={`flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 ${variantClass}`}>
      {Icon && <Icon className="w-3 h-3 shrink-0 opacity-70" />}
      <span className="text-xs font-medium">{value}</span>
      <span className="text-[10px] opacity-70">{label}</span>
    </div>
  )
}
