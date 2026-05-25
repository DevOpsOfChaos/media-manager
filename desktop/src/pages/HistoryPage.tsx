import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { userFriendlyError } from "@/lib/error-utils"
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
  type HistoryListPayload,
  type HistoryRunEntry,
} from "@/lib/tauri-bridge"
import { EmptyState } from "@/components/shared/EmptyState"

export default function HistoryPage() {
  const t = useT()
  const [data, setData] = useState<HistoryListPayload | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState("")
  const navigate = useNavigate()
  const [filterCommand, setFilterCommand] = useState<string>("all")
  const [filterMode, setFilterMode] = useState<string>("all")

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

  const availableCommands = useMemo(() => {
    if (!data?.runs) return []
    const cmds = new Set(data.runs.map(r => r.command).filter(Boolean))
    return Array.from(cmds).sort()
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
    return runs.filter(r => {
      if (filterCommand !== "all" && r.command !== filterCommand) return false
      if (filterMode !== "all" && r.mode !== filterMode) return false
      return true
    })
  }, [data, filter, filterCommand, filterMode])

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
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive space-y-2">
              <p>{error}</p>
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
                  title={t("No runs found", "Keine Durchläufe gefunden")}
                  description={t("Run an organize, rename, or duplicates command first. Apply-mode runs will appear here with undo support.", "Führen Sie zuerst einen Organisieren-, Umbenennen- oder Duplikate-Befehl aus. Angewendete Durchläufe erscheinen hier mit Rückgängig-Option.")}
                />
              )}

              {data && data.runs.length > 0 && (
                <>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>{data.run_count} {t("runs", "Durchläufe")}</span>
                    <span>{data.valid_count} {t("valid", "gültig")}</span>
                    {data.invalid_count > 0 && (
                      <span className="text-destructive">
                        {data.invalid_count} {t("invalid", "ungültig")}
                      </span>
                    )}
                  </div>

                  <Input
                    type="text"
                    placeholder={t("Filter by run ID, command, mode, or status...", "Nach Durchlauf-ID, Befehl, Modus oder Status filtern...")}
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="h-8 text-sm"
                  />

        <div className="flex flex-wrap items-center gap-2 mb-4">
          <select
            value={filterCommand}
            onChange={(e) => setFilterCommand(e.target.value)}
            className="text-xs rounded-md border border-border bg-background px-2 py-1.5 text-foreground"
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
          >
            <option value="all">{t("All modes", "Alle Modi")}</option>
            <option value="apply">{t("Apply", "Anwenden")}</option>
            <option value="preview">{t("Preview", "Vorschau")}</option>
          </select>
          <span className="text-xs text-muted-foreground ml-auto">
            {filteredRuns.length} {t("of", "von")} {data?.runs?.length || 0} {t("runs", "Durchläufen")}
          </span>
        </div>

                  {filteredRuns.length === 0 ? (
                    <EmptyState
                      title={t("No matching runs", "Keine passenden Durchläufe")}
                      description={t("No runs match the current filters. Try a different command or mode.", "Keine Durchläufe entsprechen den aktuellen Filtern. Versuchen Sie einen anderen Befehl oder Modus.")}
                    />
                  ) : (
                    <div className="space-y-2">
                      {filteredRuns.map((run) => (
                        <RunRow
                          key={run.run_id}
                          run={run}
                          onClick={() => navigate(`/history/${run.run_id}`)}
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
}: {
  run: HistoryRunEntry
  onClick: () => void
}) {
  const t = useT()
  const modeLabel = run.mode === "apply" ? t("Applied", "Angewendet") : run.mode === "preview" ? t("Preview", "Vorschau") : "—"
  const modeVariant = run.mode === "apply" ? "default" : "secondary" as const

  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
    >
      <span
        className={`inline-flex size-2 shrink-0 rounded-full ${
          run.valid ? (run.exit_code === 0 ? "bg-green-500" : "bg-yellow-500") : "bg-destructive"
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
