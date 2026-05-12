import { useCallback, useEffect, useState } from "react"
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
                      </button>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        No runs yet. Use the CLI to organize or scan files,
                        then see results here.
                      </p>
                    )}
                  </>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    {data.historyError
                      ? "Could not load history."
                      : "Loading..."}
                  </p>
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
