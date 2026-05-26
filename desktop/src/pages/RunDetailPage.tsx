import { useCallback, useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { RotateCcw } from "lucide-react"
import { useT } from "@/lib/i18n"
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
import { historyGet, undoPreview, undoApply, type HistoryDetail } from "@/lib/tauri-bridge"
import type { UndoExecutionResult } from "@/types"

export default function RunDetailPage() {
  const t = useT()
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
    detail?.mode === "apply" ? t("Applied", "Angewendet") : detail?.mode === "preview" ? t("Preview", "Vorschau") : "—"

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

  useEffect(() => {
    if (!undoPreviewResult || undoResult) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setUndoPreviewResult(null)
      if (e.key === "Enter") handleUndoApply()
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [undoPreviewResult, undoResult, handleUndoApply])

  return (
    <>
      <PageHeader title={t(`Run: ${runId ?? "unknown"}`, `Durchlauf: ${runId ?? "unbekannt"}`)} />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-3xl space-y-4">
          <div className="flex items-center gap-2">
            {detail?.has_journal && (
              <>
              <Button onClick={handleUndoPreview} disabled={undoLoading} variant="destructive" size="sm">
                <RotateCcw className="w-4 h-4 mr-1" />
                {t("Undo", "Rückgängig")}
              </Button>
              <span className="text-xs text-muted-foreground hidden sm:inline">{t("→ preview, then confirm", "→ Vorschau, dann bestätigen")}</span>
              <kbd className="hidden lg:inline-flex items-center px-1.5 py-0.5 text-[10px] rounded border border-border ml-2 text-muted-foreground">Ctrl+Z</kbd>
              </>
            )}
            <Button variant="outline" size="sm" onClick={() => navigate("/history")}>
              {t("Back to history", "Zurück zum Verlauf")}
            </Button>
            <Button variant="outline" size="sm" onClick={load} disabled={loading}>
              {loading ? (
                <span className="inline-flex items-center gap-1">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                  {t("Loading...", "Lädt...")}
                </span>
              ) : t("Refresh", "Aktualisieren")}
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
                <div className="flex items-center justify-center gap-3">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  <span className="text-sm text-muted-foreground">{t("Loading run details...", "Lade Durchlauf-Details...")}</span>
                </div>
              </CardContent>
            </Card>
          )}

          {detail && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>{t("Overview", "Übersicht")}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <InfoRow label={t("Run ID", "Durchlauf-ID")} value={detail.run_id} mono />
                  <InfoRow label={t("Command", "Befehl")} value={detail.command ?? "—"} />
                  <InfoRow label={t("Mode", "Modus")}>
                    <Badge variant={detail.mode === "apply" ? "default" : "secondary"}>
                      {modeLabel}
                    </Badge>
                  </InfoRow>
                  <InfoRow label={t("Status", "Status")} value={detail.status ?? "—"} />
                  <InfoRow label={t("Created", "Erstellt")} value={detail.created_at_utc ?? "—"} />
                  <InfoRow
                    label={t("Exit code", "Exit-Code")}
                    value={detail.exit_code !== null ? String(detail.exit_code) : "—"}
                  />
                  {detail.next_action && (
                    <InfoRow label={t("Next action", "Nächste Aktion")} value={detail.next_action} />
                  )}
                  <InfoRow label={t("Valid", "Gültig")} value={detail.valid ? t("Yes", "Ja") : t("No", "Nein")} />
                {detail.has_journal && (
                  <>
                    <InfoRow label={t("Journal", "Journal")}>
                      <span className="text-sm text-green-400">{t("Available", "Verfügbar")}</span>
                    </InfoRow>
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {t(
                          "An execution journal records every file operation from the apply run — source paths, target paths, and how to reverse each action. Click Undo to preview and reverse these operations.",
                          "Ein Ausführungsjournal zeichnet jede Dateioperation des Anwendungsdurchlaufs auf — Quellpfade, Zielpfade und wie jede Aktion rückgängig gemacht werden kann. Klicken Sie Rückgängig, um diese Operationen in der Vorschau zu sehen und rückgängig zu machen."
                        )}
                      </p>
                    </div>
                  </>
                )}
                  {detail.missing_files.length > 0 && (
                    <InfoRow
                      label={t("Missing files", "Fehlende Dateien")}
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
                    <CardTitle>{t("Summary", "Zusammenfassung")}</CardTitle>
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
                    <CardTitle>{t("Outcome", "Ergebnis")}</CardTitle>
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
                    <CardTitle>{t("Command", "Befehl")}</CardTitle>
                    <CardDescription>
                      {t("CLI arguments and metadata for this run.", "CLI-Argumente und Metadaten für diesen Durchlauf.")}
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
              <CardHeader><CardTitle className="text-yellow-400">{t("Undo Preview", "Vorschau Rückgängig")}</CardTitle></CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>{t(`This will reverse ${undoPreviewResult.planned_count} file operations.`, `Dies wird ${undoPreviewResult.planned_count} Dateioperationen rückgängig machen.`)}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {t(`${undoPreviewResult.reversible_entry_count} of ${undoPreviewResult.planned_count} operations can be safely reversed.`, `${undoPreviewResult.reversible_entry_count} von ${undoPreviewResult.planned_count} Operationen können sicher rückgängig gemacht werden.`)}
                  {undoPreviewResult.planned_count - undoPreviewResult.reversible_entry_count > 0
                    ? t(`${undoPreviewResult.planned_count - undoPreviewResult.reversible_entry_count} operations cannot be undone (files may no longer exist at their original location).`, `${undoPreviewResult.planned_count - undoPreviewResult.reversible_entry_count} Operationen können nicht rückgängig gemacht werden (Dateien existieren möglicherweise nicht mehr am ursprünglichen Ort).`)
                    : t("All operations can be fully reversed.", "Alle Operationen können vollständig rückgängig gemacht werden.")}
                </p>
                <div className="flex gap-2 mt-2">
                  <Button onClick={handleUndoApply} variant="default" size="sm">{t("Confirm Undo", "Rückgängig bestätigen")}</Button>
                  <Button onClick={() => setUndoPreviewResult(null)} variant="ghost" size="sm">{t("Cancel", "Abbrechen")}</Button>
                </div>
              </CardContent>
            </Card>
          )}
          {undoResult && (
            <Card className={undoResult.error_count === 0 ? "border-green-500/50" : "border-red-500/50 mt-4"}>
              <CardHeader><CardTitle className={undoResult.error_count === 0 ? "text-green-400" : "text-red-400"}>{t("Undo Result", "Ergebnis Rückgängig")}</CardTitle></CardHeader>
              <CardContent className="space-y-1 text-sm">
                <p>{t("Undone:", "Rückgängig:")} {undoResult.undone_count}</p>
                <p>{t("Skipped:", "Übersprungen:")} {undoResult.skipped_count}</p>
                {undoResult.error_count > 0 && <p className="text-red-400">{t("Errors:", "Fehler:")} {undoResult.error_count}</p>}
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
