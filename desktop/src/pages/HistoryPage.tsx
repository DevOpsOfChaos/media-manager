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
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  historyList,
  type HistoryListPayload,
  type HistoryRunEntry,
} from "@/lib/tauri-bridge"

export default function HistoryPage() {
  const [data, setData] = useState<HistoryListPayload | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await historyList()
      setData(result)
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return (
    <>
      <PageHeader title="History" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Run History</CardTitle>
                  <CardDescription>
                    Browse past runs, inspect results, and undo operations.
                  </CardDescription>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={load}
                  disabled={loading}
                >
                  {loading ? "Loading..." : "Refresh"}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading && !data && (
                <p className="text-sm text-muted-foreground">Loading runs...</p>
              )}

              {data && data.runs.length === 0 && (
                <p className="text-sm text-muted-foreground">
                  No runs found. Run a command from the CLI to see history here.
                </p>
              )}

              {data && data.runs.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-3 text-xs text-muted-foreground mb-2">
                    <span>{data.run_count} runs</span>
                    <span>{data.valid_count} valid</span>
                    {data.invalid_count > 0 && (
                      <span className="text-destructive">
                        {data.invalid_count} invalid
                      </span>
                    )}
                  </div>

                  {data.runs.map((run) => (
                    <RunRow
                      key={run.run_id}
                      run={run}
                      onClick={() => navigate(`/history/${run.run_id}`)}
                    />
                  ))}
                </div>
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
  const modeLabel = run.mode === "apply" ? "Applied" : run.mode === "preview" ? "Preview" : "—"
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
          <span>{run.command ?? "unknown"}</span>
          {run.status && <span>· {run.status}</span>}
          {run.created_at_utc && <span>· {run.created_at_utc.slice(0, 10)}</span>}
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
