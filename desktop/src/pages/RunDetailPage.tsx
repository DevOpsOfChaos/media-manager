import { useCallback, useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
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
import { historyGet, type HistoryDetail } from "@/lib/tauri-bridge"

export default function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const navigate = useNavigate()
  const [detail, setDetail] = useState<HistoryDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!runId) return
    setLoading(true)
    setError(null)
    try {
      const result = await historyGet(runId)
      setDetail(result)
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }, [runId])

  useEffect(() => {
    load()
  }, [load])

  const modeLabel =
    detail?.mode === "apply" ? "Applied" : detail?.mode === "preview" ? "Preview" : "—"

  return (
    <>
      <PageHeader title={`Run: ${runId ?? "unknown"}`} />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate("/history")}>
              Back to history
            </Button>
            <Button variant="outline" size="sm" onClick={load} disabled={loading}>
              {loading ? "Loading..." : "Refresh"}
            </Button>
          </div>

          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}

          {loading && !detail && (
            <Card>
              <CardContent className="py-8">
                <p className="text-sm text-muted-foreground">Loading run details...</p>
              </CardContent>
            </Card>
          )}

          {detail && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Overview</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <InfoRow label="Run ID" value={detail.run_id} mono />
                  <InfoRow label="Command" value={detail.command ?? "—"} />
                  <InfoRow label="Mode">
                    <Badge variant={detail.mode === "apply" ? "default" : "secondary"}>
                      {modeLabel}
                    </Badge>
                  </InfoRow>
                  <InfoRow label="Status" value={detail.status ?? "—"} />
                  <InfoRow label="Created" value={detail.created_at_utc ?? "—"} />
                  <InfoRow
                    label="Exit code"
                    value={detail.exit_code !== null ? String(detail.exit_code) : "—"}
                  />
                  {detail.next_action && (
                    <InfoRow label="Next action" value={detail.next_action} />
                  )}
                  <InfoRow label="Valid" value={detail.valid ? "Yes" : "No"} />
                  {detail.has_journal && (
                    <InfoRow label="Journal" value="Available (undo possible)" />
                  )}
                  {detail.missing_files.length > 0 && (
                    <InfoRow
                      label="Missing files"
                      value={detail.missing_files.join(", ")}
                    />
                  )}
                  {detail.errors.length > 0 && (
                    <div className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive">
                      {detail.errors.join("; ")}
                    </div>
                  )}
                </CardContent>
              </Card>

              {detail.summary && (
                <Card>
                  <CardHeader>
                    <CardTitle>Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="whitespace-pre-wrap text-xs font-mono text-muted-foreground max-h-64 overflow-y-auto">
                      {detail.summary}
                    </pre>
                  </CardContent>
                </Card>
              )}

              {detail.report_outcome && (
                <Card>
                  <CardHeader>
                    <CardTitle>Outcome</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="whitespace-pre-wrap text-xs font-mono text-muted-foreground max-h-64 overflow-y-auto">
                      {JSON.stringify(detail.report_outcome, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
              )}

              {detail.command_json && (
                <Card>
                  <CardHeader>
                    <CardTitle>Command</CardTitle>
                    <CardDescription>
                      CLI arguments and metadata for this run.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <pre className="whitespace-pre-wrap text-xs font-mono text-muted-foreground max-h-64 overflow-y-auto">
                      {JSON.stringify(detail.command_json, null, 2)}
                    </pre>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </main>
    </>
  )
}

function InfoRow({
  label,
  value,
  mono,
  children,
}: {
  label: string
  value?: string
  mono?: boolean
  children?: React.ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-sm text-muted-foreground shrink-0">{label}</span>
      {children ?? (
        <span
          className={`text-sm text-right truncate ${mono ? "font-mono" : ""}`}
        >
          {value}
        </span>
      )}
    </div>
  )
}
