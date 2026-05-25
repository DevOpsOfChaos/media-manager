import { useCallback, useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
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
import {
  UNSUPPORTED_FEATURES,
  type ReviewSourceKind,
  type ReviewDecisionDraft,
} from "@/types"
import { useReviewStore } from "@/stores/review-store"

export default function ReviewWorkbenchPage() {
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
      <PageHeader title="Review Workbench">
        {groups.length > 0 && (
          <Button variant="outline" size="sm" onClick={reset}>
            Reset session
          </Button>
        )}
      </PageHeader>
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-4xl space-y-4">
          {/* Safety banner */}
          {persistError ? (
            <div className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950 px-4 py-3 text-sm text-red-800 dark:text-red-200">
              <p className="font-medium">Save failed</p>
              <p className="text-xs">{persistError}</p>
            </div>
          ) : sessionPath ? (
            <div className="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950 px-4 py-3 text-sm text-green-800 dark:text-green-200">
              <p className="font-medium">Decisions are persisted to disk.</p>
              <p className="text-xs">Draft decisions are saved automatically and restored when you return.</p>
            </div>
          ) : (
            <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
              <p className="font-medium">No session active.</p>
              <p className="text-xs">Run a scan first to load candidates. Decisions will be persisted to disk.</p>
            </div>
          )}

          {/* Source selection + status */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Source</CardTitle>
                <CardDescription className="text-xs">
                  Select which preview results to review.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button
                    variant={activeSourceKind === "exact_duplicates" ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSourceSelect("exact_duplicates")}
                  >
                    Exact duplicates
                  </Button>
                  <Button
                    variant={activeSourceKind === "similar_images" ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleSourceSelect("similar_images")}
                  >
                    Similar images
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Status</CardTitle>
                <CardDescription className="text-xs">
                  Current session overview.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 text-xs">
                  <Badge variant="secondary">
                    {totalCandidates} candidates
                  </Badge>
                  <Badge variant={reviewedCount > 0 ? "default" : "secondary"}>
                    {reviewedCount} reviewed
                  </Badge>
                  <Badge variant={sessionPath ? "default" : "secondary"}>{sessionPath ? "persisted" : "in-memory only"}</Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Groups or empty state */}
          {filteredGroups.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Candidates ({filteredGroups.length} groups)</CardTitle>
                <CardDescription>
                  Decisions are saved to disk automatically.
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
                            {group.candidates.length} candidates
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {group.source_kind === "exact_duplicates" ? "exact" : "similar"}
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
                                      ? "keep"
                                      : d === "remove_later"
                                        ? "remove"
                                        : "ignore"}
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
                    Showing first 50 of {filteredGroups.length} groups.
                  </p>
                )}
              </CardContent>
            </Card>
          ) : (
            <EmptyState
              title="No candidates loaded"
              description="Run a duplicate scan first, then return here. Decisions are persisted to disk and restored when you come back."
            />
          )}

          {/* Unsupported features */}
          <Card>
            <CardHeader>
              <CardTitle>Review decision persistence coming soon</CardTitle>
              <CardDescription>
                These features are planned but require additional safety
                infrastructure before they can be enabled.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {UNSUPPORTED_FEATURES.map((f) => (
                  <div key={f.feature} className="flex items-start gap-3 rounded-lg border p-3 opacity-60">
                    <Badge variant="secondary" className="text-xs shrink-0 mt-0.5">
                      planned
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

          {/* Quick links */}
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => navigate("/duplicates")}>
              Go to Duplicates Preview
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate("/history")}>
              Go to History
            </Button>
          </div>
        </div>
      </main>
    </>
  )
}
