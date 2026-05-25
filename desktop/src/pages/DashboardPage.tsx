import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
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
import {
  runtimeDiagnostics,
  settingsRead,
  historyList,
  type RuntimeDiagnostics,
  type HistoryListPayload,
  type HistoryRunEntry,
} from "@/lib/tauri-bridge"
import type { GuiSettings } from "@/types"
import { EmptyState } from "@/components/shared/EmptyState"

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

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData>({
    diag: null,
    diagError: null,
    settings: null,
    settingsError: null,
    history: null,
    historyError: null,
  })
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

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
      <PageHeader title="Dashboard">
        <Button
          variant="outline"
          size="sm"
          onClick={load}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh"}
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

          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
              <Card className="p-4">
                <p className="text-2xl font-bold">{stats.totalRuns}</p>
                <p className="text-xs text-muted-foreground">Total runs</p>
              </Card>
              <Card className="p-4">
                <p className="text-2xl font-bold text-green-400">{stats.applyRuns}</p>
                <p className="text-xs text-muted-foreground">Applied runs</p>
              </Card>
              <Card className="p-4">
                <p className="text-2xl font-bold">{stats.successRate}%</p>
                <p className="text-xs text-muted-foreground">Success rate</p>
              </Card>
              <Card className="p-4">
                <p className="text-2xl font-bold">{stats.totalActions}</p>
                <p className="text-xs text-muted-foreground">Total actions</p>
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
                <CardTitle>System Status</CardTitle>
                <CardDescription>
                  Python bridge health and environment.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <StatusRow
                  label="Python bridge"
                  ok={pythonOk}
                  detail={
                    data.diag
                      ? data.diag.python_version?.split(" ")[0] ?? "reachable"
                      : data.diagError
                        ? "unreachable"
                        : "checking..."
                  }
                />
                <StatusRow
                  label="Settings file"
                  ok={data.diag?.settings_file_exists}
                  detail={
                    data.diag?.settings_file_exists
                      ? "found"
                      : data.diag
                        ? "not found"
                        : "—"
                  }
                />
                <StatusRow
                  label="Project root"
                  ok={!!data.diag?.project_root}
                  detail={data.diag?.project_root ? "resolved" : "—"}
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
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Run history and operation summary.
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
                        total runs
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-sm">
                      <Badge variant="secondary">
                        {data.history.valid_count} valid
                      </Badge>
                      {data.history.invalid_count > 0 && (
                        <Badge variant="destructive">
                          {data.history.invalid_count} invalid
                        </Badge>
                      )}
                    </div>

                    {latestRun ? (
                      <button
                        onClick={() =>
                          navigate(`/history/${latestRun.run_id}`)
                        }
                        className="w-full rounded-lg border p-3 text-left hover:bg-muted/50 transition-colors"
                      >
                        <p className="text-xs text-muted-foreground">
                          Latest run
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
                              ? "Applied"
                              : latestRun.mode === "preview"
                                ? "Preview"
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
                                {latestRun.review_candidate_count} items need review
                              </p>
                            )}
                          </div>
                        )}
                      </button>
                    ) : (
                      <EmptyState
                        title="No activity yet"
                        description="Run your first organize, duplicates scan, or cleanup workflow to see results here."
                      />
                    )}
                  </>
                ) : (
                  <div className="text-sm text-muted-foreground">
                    {data.historyError
                      ? "Could not load history."
                      : (
                        <span className="inline-flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                          Loading...
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
                <CardTitle>Configuration</CardTitle>
                <CardDescription>
                  Current settings at a glance.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Language</p>
                    <p className="font-medium">
                      {data.settings.language === "de" ? "Deutsch" : "English"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Theme</p>
                    <p className="font-medium">
                      {data.settings.theme === "modern-light"
                        ? "Light"
                        : "Dark"}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Start page</p>
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
              label="Organize"
              desc="Preview folder organization."
              onClick={() => navigate("/organize")}
            />
            <QuickNavCard
              label="Exact duplicates"
              desc="Find byte-identical files."
              onClick={() => navigate("/duplicates")}
            />
            <QuickNavCard
              label="Similar images"
              desc="Find visually similar images."
              onClick={() => navigate("/duplicates")}
            />
            <QuickNavCard
              label="Review"
              desc="Review candidates and record decisions. (coming soon)"
              disabled
              onClick={() => navigate("/review")}
            />
            <QuickNavCard
              label="History"
              desc="Browse past runs."
              onClick={() => navigate("/history")}
            />
            <QuickNavCard
              label="Settings"
              desc="Language, theme, diagnostics."
              onClick={() => navigate("/settings")}
            />
          </div>

          {/* Quick Workflows */}
          <div className="mt-6">
            <h3 className="text-sm font-medium mb-3">Quick Workflows</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {QUICK_WORKFLOWS.map((wf) => (
                <Card
                  key={wf.id}
                  className="p-4 cursor-pointer hover:border-primary/50 transition-colors"
                  onClick={() => navigate(wf.page)}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-xl">{wf.icon}</span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{wf.label}</p>
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{wf.desc}</p>
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
  return (
    <button
      onClick={onClick}
      disabled={disabled}
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
            coming soon
          </span>
        )}
      </p>
      <p className="text-xs text-muted-foreground">{desc}</p>
    </button>
  )
}
