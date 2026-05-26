import { useCallback, useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { appLocalDataDir, join } from "@tauri-apps/api/path"
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
import { EmptyState } from "@/components/shared/EmptyState"
import { ToolGuide } from "@/components/shared/ToolGuide"
import {
  UNSUPPORTED_FEATURES,
  type ReviewSourceKind,
  type ReviewDecisionDraft,
} from "@/types"
import { useReviewStore } from "@/stores/review-store"

export default function ReviewWorkbenchPage() {
  const t = useT()
  const navigate = useNavigate()
  const [, setSearchParams] = useSearchParams()
  const {
    groups,
    activeSourceKind,
    setActiveSourceKind,
    selectedGroupId,
    selectedCandidateId,
    selectGroup,
    selectCandidate,
    filterText,
    setDraftDecision,
    markReviewed,
    reset,
    sessionPath,
    setSessionPath,
    persistError,
  } = useReviewStore()

  useEffect(() => {
    if (groups.length === 0 || !activeSourceKind || sessionPath) return
    ;(async () => {
      const dir = await join(await appLocalDataDir(), "review_sessions")
      const sp = await join(dir, `${activeSourceKind}.json`)
      setSessionPath(sp)
    })()
  }, [activeSourceKind, groups.length])

  const handleSourceSelect = (kind: ReviewSourceKind | null) => {
    const next = activeSourceKind === kind ? null : kind
    setActiveSourceKind(next)
    if (next) {
      setSearchParams({ source: next })
    } else {
      setSearchParams({})
    }
  }

  const handleDecision = useCallback((candidateId: string, decision: ReviewDecisionDraft) => {
    setDraftDecision(candidateId, decision)
    markReviewed(candidateId)
  }, [setDraftDecision, markReviewed])

  const filteredGroups = groups.filter((g) => {
    if (activeSourceKind && g.source_kind !== activeSourceKind) return false
    if (!filterText.trim()) return true
    const q = filterText.toLowerCase()
    return g.candidates.some((c) => c.path.toLowerCase().includes(q))
  })

  const totalCandidates = groups.reduce((s, g) => s + g.candidates.length, 0)
  const reviewedCount = groups.reduce(
    (s, g) => s + g.candidates.filter((c) => c.role === "reviewed").length,
    0,
  )

  return (
    <>
      <PageHeader title={t("Review Workbench", "Prüf-Workbench")}>
        {groups.length > 0 && (
          <Button variant="outline" size="sm" onClick={reset}>
            {t("Reset session", "Sitzung zurücksetzen")}
          </Button>
        )}
      </PageHeader>
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-4xl space-y-4">
          <ToolGuide
            toolId="review"
            title={t("Review Workbench", "Prüf-Workbench")}
            description={t("Review and decide on scan candidates. Run a scan first to load candidates, then approve, reject, or assign to people.", "Überprüfe und entscheide über Scan-Kandidaten. Führe zuerst einen Scan durch, um Kandidaten zu laden, dann genehmige, lehne ab oder weise Personen zu.")}
            tips={[
              t("Decisions are persisted to disk and restored on return", "Entscheidungen werden gespeichert und bei Rückkehr wiederhergestellt"),
              t("Use keyboard shortcuts (A=approve, R=reject, S=skip) for speed", "Nutze Tastaturkürzel (A=genehmigen, R=ablehnen, S=überspringen) für Tempo"),
            ]}
          />
          {persistError ? (
            <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 px-4 py-3 text-sm text-red-800 dark:text-red-200">
              <p className="font-medium">{t("Save failed", "Speichern fehlgeschlagen")}</p>
              <p className="text-xs">{persistError}</p>
            </div>
          ) : sessionPath ? (
            <div className="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950 px-4 py-3 text-sm text-green-800 dark:text-green-200">
              <p className="font-medium">{t("Decisions are persisted to disk.", "Entscheidungen werden auf Datenträger gespeichert.")}</p>
              <p className="text-xs">{t("Draft decisions are saved automatically and restored when you return.", "Entscheidungsentwürfe werden automatisch gespeichert und beim Zurückkehren wiederhergestellt.")}</p>
            </div>
          ) : (
            <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
              <p className="font-medium">{t("No session active.", "Keine Sitzung aktiv.")}</p>
              <p className="text-xs">{t("Run a scan first to load candidates. Decisions will be persisted to disk.", "Führen Sie zuerst einen Scan durch, um Kandidaten zu laden. Entscheidungen werden auf Datenträger gespeichert.")}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">{t("Source", "Quelle")}</CardTitle>
                <CardDescription className="text-xs">
                  {t("Select which preview results to review.", "Wählen Sie, welche Vorschau-Ergebnisse geprüft werden sollen.")}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button
                    variant={activeSourceKind === "exact_duplicates" ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSourceSelect("exact_duplicates")}
                  >
                    {t("Exact duplicates", "Exakte Duplikate")}
                  </Button>
                  <Button
                    variant={activeSourceKind === "similar_images" ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSourceSelect("similar_images")}
                  >
                    {t("Similar images", "Ähnliche Bilder")}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">{t("Status", "Status")}</CardTitle>
                <CardDescription className="text-xs">
                  {t("Current session overview.", "Übersicht der aktuellen Sitzung.")}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 text-xs">
                  <Badge variant="secondary">
                    {totalCandidates} {t("candidates", "Kandidaten")}
                  </Badge>
                  <Badge variant={reviewedCount > 0 ? "default" : "secondary"}>
                    {reviewedCount} {t("reviewed", "geprüft")}
                  </Badge>
                  <Badge variant={sessionPath ? "default" : "secondary"}>{sessionPath ? t("persisted", "gespeichert") : t("in-memory only", "nur im Speicher")}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {groups.length === 0 && !sessionPath ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              <span className="ml-3 text-sm text-muted-foreground">{t("Waiting for scan data...", "Warte auf Scandaten...")}</span>
            </div>
          ) : groups.length === 0 ? (
            <EmptyState
              title={t("No candidates loaded", "Keine Kandidaten geladen")}
              description={t("Run a duplicate scan first, then return here. Decisions are persisted to disk and restored when you come back.", "Führen Sie zuerst einen Duplikatscan durch und kehren Sie dann hierher zurück. Entscheidungen werden gespeichert und beim Zurückkehren wiederhergestellt.")}
            />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>{t(`Candidates (${filteredGroups.length} groups)`, `Kandidaten (${filteredGroups.length} Gruppen)`)}</CardTitle>
                <CardDescription>
                  {t("Decisions are saved to disk automatically.", "Entscheidungen werden automatisch auf Datenträger gespeichert.")}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {filteredGroups.slice(0, 50).map((group) => (
                  <div key={group.id} className="rounded-lg border">
                    <button
                      onClick={() =>
                        selectGroup(
                          selectedGroupId === group.id ? null : group.id,
                        )
                      }
                      className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/50 transition-colors"
                    >
                      <span className="text-xs text-muted-foreground">
                        {selectedGroupId === group.id ? "▾" : "▸"}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-medium truncate">
                            {group.label}
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            {group.candidates.length} {t("candidates", "Kandidaten")}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {group.source_kind === "exact_duplicates" ? t("exact", "exakt") : t("similar", "ähnlich")}
                          </Badge>
                        </div>
                      </div>
                    </button>
                    {selectedGroupId === group.id && (
                      <div className="border-t px-3 py-2 space-y-1 bg-muted/20">
                        {group.candidates.map((c) => (
                          <div
                            key={c.id}
                            className={`flex items-center gap-2 py-1 rounded px-2 ${
                              selectedCandidateId === c.id ? "bg-muted" : ""
                            }`}
                          >
                            <button
                              className="flex-1 text-left truncate font-mono text-xs"
                              onClick={() => selectCandidate(c.id)}
                            >
                              {c.path.split(/[\\/]/).pop() ?? c.path}
                            </button>
                            {c.distance != null && (
                              <Badge
                                variant={
                                  c.distance === 0 ? "default" : "secondary"
                                }
                                className="text-xs shrink-0"
                              >
                                d={c.distance}
                              </Badge>
                            )}
                            <Badge
                              variant={
                                c.role === "reviewed"
                                  ? "default"
                                  : "secondary"
                              }
                              className="text-xs shrink-0"
                            >
                              {c.role}
                            </Badge>
                            {/* Draft decision controls */}
                            <div className="flex gap-1 shrink-0">
                              {(["keep_reference", "remove_later", "ignore"] as const).map(
                                (d) => (
                                  <Button
                                    key={d}
                                    variant="ghost"
                                    size="sm"
                                    disabled={c.role === "reviewed"}
                                    className={`h-5 px-1.5 text-[10px] ${c.role === "reviewed" ? "opacity-50" : ""}`}
                                    onClick={() => handleDecision(c.id, d)}
                                  >
                                    {d === "keep_reference"
                                      ? t("keep", "behalten")
                                      : d === "remove_later"
                                        ? t("remove", "entfernen")
                                        : t("ignore", "ignorieren")}
                                  </Button>
                                ),
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                {filteredGroups.length > 50 && (
                  <p className="text-xs text-muted-foreground">
                    {t(`Showing first 50 of ${filteredGroups.length} groups.`, `Zeige erste 50 von ${filteredGroups.length} Gruppen.`)}
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>{t("Planned features", "Geplante Funktionen")}</CardTitle>
              <CardDescription>
                {t("These features are planned but require additional safety infrastructure before they can be enabled. Decision drafts are already persisted to disk via the session bridge.", "Diese Funktionen sind geplant, benötigen aber zusätzliche Sicherheitsinfrastruktur. Entscheidungsentwürfe werden bereits über die Sitzungsbrücke gespeichert.")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {UNSUPPORTED_FEATURES.map((f) => (
                  <div key={f.feature} className="flex items-start gap-3 rounded-lg border p-3 opacity-60">
                    <Badge variant="secondary" className="text-xs shrink-0 mt-0.5">
                      {t("planned", "geplant")}
                    </Badge>
                    <div>
                      <p className="text-sm font-medium">{f.feature}</p>
                      <p className="text-xs text-muted-foreground">{f.reason}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate("/duplicates")}>
              {t("Go to Duplicates Preview", "Zur Duplikatvorschau")}
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate("/history")}>
              {t("Go to History", "Zum Verlauf")}
            </Button>
          </div>
        </div>
      </main>
    </>
  )
}
