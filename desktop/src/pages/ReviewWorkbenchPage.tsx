import { useEffect, useState } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { invoke, convertFileSrc } from "@tauri-apps/api/core"
import { appLocalDataDir, join } from "@tauri-apps/api/path"
import { PageHeader } from "@/components/layout/PageHeader"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { EmptyState } from "@/components/shared/EmptyState"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Check, EyeOff, Trash2, Loader2 } from "lucide-react"
import type { ReviewSourceKind } from "@/types"
import { useReviewStore } from "@/stores/review-store"

export default function ReviewWorkbenchPage() {
  const t = useT()
  const navigate = useNavigate()
  const [, setSearchParams] = useSearchParams()
  const {
    groups, activeSourceKind, setActiveSourceKind,
    selectedGroupId, selectGroup,
    filterText, setFilterText, setDraftDecision, markReviewed,
    reset, sessionPath, setSessionPath,
  } = useReviewStore()

  const [applyDialogOpen, setApplyDialogOpen] = useState(false)
  const [applying, setApplying] = useState(false)

  // Initialize session
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
    if (next) setSearchParams({ source: next })
    else setSearchParams({})
  }

  // Count decisions
  const stats = groups.reduce((acc, g) => {
    g.candidates.forEach(c => {
      if (c.draft_decision === "keep_reference") acc.keep++
      else if (c.draft_decision === "remove_later") acc.remove++
      else if (c.draft_decision === "ignore") acc.ignore++
      if (c.role === "reviewed") acc.reviewed++
    })
    return acc
  }, { keep: 0, remove: 0, ignore: 0, reviewed: 0, total: groups.reduce((s, g) => s + g.candidates.length, 0) })

  // Apply decisions
  const handleApply = async () => {
    setApplying(true)
    const toRemove = groups.flatMap(g => 
      g.candidates.filter(c => c.draft_decision === "remove_later").map(c => c.path)
    )
    try {
      await invoke("review_apply_decisions", { 
        sessionPath, 
        toKeep: groups.flatMap(g => g.candidates.filter(c => c.draft_decision === "keep_reference" || c.draft_decision === "ignore").map(c => ({ path: c.path, decision: c.draft_decision }))),
        toRemove 
      })
    } catch (e) {
      console.error("apply failed", e)
    }
    setApplying(false)
    setApplyDialogOpen(false)
  }

  return (
    <>
      <PageHeader title={t("Review Workbench", "Prüf-Workbench")}>
        {groups.length > 0 && (
          <div className="flex gap-2">
            <Badge variant="outline">{stats.total} {t("total", "gesamt")}</Badge>
            <Badge className="bg-green-100 text-green-800">{stats.keep} {t("keep", "behalten")}</Badge>
            <Badge className="bg-red-100 text-red-800">{stats.remove} {t("remove", "entfernen")}</Badge>
            <Badge variant="outline">{stats.reviewed} {t("reviewed", "geprüft")}</Badge>
            {stats.remove > 0 && (
              <Button size="sm" variant="destructive" onClick={() => setApplyDialogOpen(true)}>
                <Trash2 className="h-3 w-3 mr-1" />{t("Apply", "Anwenden")} ({stats.remove})
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={reset}>{t("Reset", "Zurücksetzen")}</Button>
          </div>
        )}
      </PageHeader>

      <main className="flex flex-1 gap-4 p-6">
        <div className="flex-1 max-w-5xl space-y-4">
          {/* Source selector */}
          <div className="flex gap-2 flex-wrap">
            <Button variant={activeSourceKind === "exact_duplicates" ? "default" : "outline"} size="sm" onClick={() => handleSourceSelect("exact_duplicates")}>
              {t("Exact duplicates", "Exakte Duplikate")}
            </Button>
            <Button variant={activeSourceKind === "similar_images" ? "default" : "outline"} size="sm" onClick={() => handleSourceSelect("similar_images")}>
              {t("Similar images", "Ähnliche Bilder")}
            </Button>
            <Button variant="outline" size="sm" onClick={() => navigate("/duplicates")}>
              {t("Run new scan", "Neuer Scan")}
            </Button>
            <Input value={filterText} onChange={e => setFilterText(e.target.value)}
              placeholder={t("Filter by path...", "Nach Pfad filtern...")}
              className="text-xs h-8 w-48 ml-auto" />
          </div>

          {/* No data */}
          {groups.length === 0 && (
            <EmptyState
              title={t("No review data", "Keine Prüfdaten")}
              description={t("Run a duplicate scan first. Results appear here for review.", "Führe erst einen Duplikatscan durch. Ergebnisse erscheinen hier zur Prüfung.")}
              action={<Button size="sm" variant="outline" onClick={() => navigate("/duplicates")}>{t("Go to Duplicates", "Zu Duplikaten")}</Button>}
            />
          )}

          {/* Candidate list */}
          {groups.filter(g => {
            if (activeSourceKind && g.source_kind !== activeSourceKind) return false
            if (!filterText.trim()) return true
            return g.candidates.some(c => c.path.toLowerCase().includes(filterText.toLowerCase()))
          }).slice(0, 100).map(group => (
            <Card key={group.id} className="overflow-hidden">
              <button onClick={() => selectGroup(selectedGroupId === group.id ? null : group.id)}
                className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/30">
                <span>{selectedGroupId === group.id ? "▾" : "▸"}</span>
                <span className="font-mono text-xs truncate flex-1">{group.label}</span>
                <Badge variant="secondary" className="text-[10px]">{group.candidates.length}</Badge>
              </button>
              {selectedGroupId === group.id && (
                <div className="border-t p-2 space-y-1 bg-muted/10">
                  {group.candidates.map(c => (
                    <div key={c.id} className={`flex items-center gap-2 p-1.5 rounded ${c.role === "reviewed" ? "opacity-60" : ""}`}>
                      {/* Thumbnail */}
                      <div className="w-12 h-12 rounded bg-muted overflow-hidden shrink-0">
                        <img
                          src={convertFileSrc(c.path)}
                          className="w-full h-full object-cover"
                          loading="lazy"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = "none"
                            if ((e.target as HTMLImageElement).parentElement) {
                              (e.target as HTMLImageElement).parentElement!.classList.add("fallback-icon")
                            }
                          }}
                        />
                      </div>
                      {/* Path */}
                      <span className="text-[11px] font-mono truncate flex-1" title={c.path}>
                        {c.path.split(/[\\/]/).pop()}
                      </span>
                      {/* Distance */}
                      {c.distance != null && (
                        <Badge variant="secondary" className="text-[10px] shrink-0">d={c.distance}</Badge>
                      )}
                      {/* Decision buttons */}
                      <div className="flex gap-0.5 shrink-0">
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant={c.draft_decision === "keep_reference" ? "default" : "ghost"}
                              size="icon" className="h-7 w-7" onClick={() => { setDraftDecision(c.id, "keep_reference"); markReviewed(c.id) }}>
                              <Check className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>{t("Keep", "Behalten")}</TooltipContent>
                        </Tooltip>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant={c.draft_decision === "remove_later" ? "destructive" : "ghost"}
                              size="icon" className="h-7 w-7" onClick={() => { setDraftDecision(c.id, "remove_later"); markReviewed(c.id) }}>
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>{t("Remove", "Entfernen")}</TooltipContent>
                        </Tooltip>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant={c.draft_decision === "ignore" ? "secondary" : "ghost"}
                              size="icon" className="h-7 w-7" onClick={() => { setDraftDecision(c.id, "ignore"); markReviewed(c.id) }}>
                              <EyeOff className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>{t("Ignore", "Ignorieren")}</TooltipContent>
                        </Tooltip>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          ))}

          {/* Apply confirmation dialog */}
          <Dialog open={applyDialogOpen} onOpenChange={setApplyDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t("Apply review decisions?", "Prüfentscheidungen anwenden?")}</DialogTitle>
                <DialogDescription>
                  {t("This will move files marked for removal to the trash. This action can be undone from the History page.", "Dies verschiebt zum Entfernen markierte Dateien in den Papierkorb. Die Aktion kann über die Verlaufsseite rückgängig gemacht werden.")}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-1 text-sm">
                <p>✅ {stats.keep} {t("files kept", "Dateien behalten")}</p>
                <p className="text-red-500">🗑️ {stats.remove} {t("files to remove", "Dateien zum Entfernen")}</p>
                <p className="text-muted-foreground">👁️ {stats.ignore} {t("files ignored", "Dateien ignoriert")}</p>
              </div>
              <DialogFooter>
                <Button variant="outline" size="sm" onClick={() => setApplyDialogOpen(false)}>{t("Cancel", "Abbrechen")}</Button>
                <Button variant="destructive" size="sm" onClick={handleApply} disabled={applying}>
                  {applying ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <Trash2 className="h-3 w-3 mr-1" />}
                  {t("Remove files", "Dateien entfernen")}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </main>
    </>
  )
}
