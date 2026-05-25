import { useCallback, useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { RotateCcw } from "lucide-react"
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
import { undoPreview, undoApply } from "@/lib/tauri-bridge"
import type { UndoExecutionResult } from "@/types"

export default function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>()
  const navigate = useNavigate()
  const [detail, setDetail] = useState<HistoryDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [undoLoading, setUndoLoading] = useState(false)
  const [undoPreviewResult, setUndoPreviewResult] = useState<UndoExecutionResult | null>(null)
  const [undoResult, setUndoResult] = useState<UndoExecutionResult | null>(null)

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

  const handleUndoPreview = useCallback(async () => {
    if (!detail?.has_journal || !runId) return
    setUndoLoading(true)
    try {
      const preview = await undoPreview(runId)
      setUndoPreviewResult(preview)
    } catch (e) {
      setError(String(e))
    } finally {
      setUndoLoading(false)
    }
  }, [runId, detail?.has_journal])

  const handleUndoApply = useCallback(async () => {
    if (!runId) return
    setUndoLoading(true)
    try {
      const result = await undoApply(runId)
      setUndoResult(result)
      setUndoPreviewResult(null)
    } catch (e) {
      setError(String(e))
    } finally {
      setUndoLoading(false)
    }
  }, [runId])

  return (
    <>
      <PageHeader title={`Run: ${runId ?? "unknown"}`} />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          <div className="flex items-center gap-2">
            {detail?.has_journal && (
              <>
              <Button onClick={handleUndoPreview} disabled={undoLoading} variant="destructive" size="sm">
                <RotateCcw className="w-4 h-4 mr-1" />
                Undo
              </Button>
              <span className="text-xs text-muted-foreground hidden sm:inline">→ preview, then confirm</span>
              <kbd className="hidden lg:inline-flex items-center px-1.5 py-0.5 text-[10px] rounded border border-border ml-2 text-muted-foreground">Ctrl+Z</kbd>
              </>
            )}
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
                  <>
                    <InfoRow label="Journal">
                      <span className="text-sm text-green-400">Available</span>
                    </InfoRow>
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        An execution journal records every file operation from the apply run —
                        source paths, target paths, and how to reverse each action.
                        Click <span className="font-medium text-foreground">Undo</span> to preview
                        and reverse these operations.
                      </p>
                    </div>
                  </>
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
          {undoPreviewResult && !undoResult && (
            <Card className="border-yellow-500/50 mt-4">
              <CardHeader><CardTitle className="text-yellow-400">Undo Preview</CardTitle></CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>This will reverse {undoPreviewResult.planned_count} file operations.</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {undoPreviewResult.reversible_entry_count} of {undoPreviewResult.planned_count} operations can be safely reversed.
                  {undoPreviewResult.planned_count - undoPreviewResult.reversible_entry_count > 0
                    ? `${undoPreviewResult.planned_count - undoPreviewResult.reversible_entry_count} operations cannot be undone (files may no longer exist at their original location).`
                    : "All operations can be fully reversed."}
                </p>
                <div className="flex gap-2 mt-2">
                  <Button onClick={handleUndoApply} variant="default" size="sm">Confirm Undo</Button>
                  <Button onClick={() => setUndoPreviewResult(null)} variant="ghost" size="sm">Cancel</Button>
                </div>
              </CardContent>
            </Card>
          )}
          {undoResult && (
            <Card className={undoResult.error_count === 0 ? "border-green-500/50" : "border-red-500/50 mt-4"}>
              <CardHeader><CardTitle className={undoResult.error_count === 0 ? "text-green-400" : "text-red-400"}>Undo Result</CardTitle></CardHeader>
              <CardContent className="space-y-1 text-sm">
                <p>Undone: {undoResult.undone_count}</p>
                <p>Skipped: {undoResult.skipped_count}</p>
                {undoResult.error_count > 0 && <p className="text-red-400">Errors: {undoResult.error_count}</p>}
              </CardContent>
            </Card>
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
