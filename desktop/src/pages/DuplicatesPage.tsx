import { useCallback, useEffect, useMemo, useState } from "react"
import { CheckSquare, Square, Trash2, Info } from "lucide-react"
import { convertFileSrc } from "@tauri-apps/api/core"
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
import { Input } from "@/components/ui/input"
import { ErrorBanner } from "@/components/shared/ErrorBanner"
import { EmptyState } from "@/components/shared/EmptyState"
import { duplicateScan, similarImagesScan, duplicatesApply } from "@/lib/tauri-bridge"
import { useSettingsStore } from "@/stores/settings-store"
import type {
  DuplicatesPreviewResponse,
  SimilarImagesPreviewResponse,
  ExactDuplicateGroup,
  SimilarImageGroup,
} from "@/types"

type Tab = "exact" | "similar"

function FileThumbnail({ path, size = 80 }: { path: string; size?: number }) {
  const [loaded, setLoaded] = useState(false)
  const [errored, setErrored] = useState(false)
  const src = convertFileSrc(path)

  if (errored) {
    return (
      <div
        className="flex items-center justify-center bg-muted rounded text-muted-foreground text-[10px]"
        style={{ width: size, height: size, minWidth: size }}
      >
        no preview
      </div>
    )
  }

  return (
    <div className="relative" style={{ width: size, height: size, minWidth: size }}>
      {!loaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted rounded">
          <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      <img
        src={src}
        alt=""
        className="rounded object-cover"
        style={{ width: size, height: size, opacity: loaded ? 1 : 0 }}
        onLoad={() => setLoaded(true)}
        onError={() => setErrored(true)}
        loading="lazy"
      />
    </div>
  )
}

export default function DuplicatesPage() {
  const [sourceDir, setSourceDir] = useState(() => localStorage.getItem("default_source_dir") || "")
  const [tab, setTab] = useState<Tab>("exact")
  const [exactPreview, setExactPreview] = useState<DuplicatesPreviewResponse | null>(null)
  const [similarPreview, setSimilarPreview] = useState<SimilarImagesPreviewResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filterPath, setFilterPath] = useState("")
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())
  const [maxDistance, setMaxDistance] = useState(6)
  const [maxImages, setMaxImages] = useState(500)
  const [maxPairs, setMaxPairs] = useState(150_000)
  const { settings } = useSettingsStore()
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [deleteResult, setDeleteResult] = useState<{ executed_rows: number; error_rows: number } | null>(null)
  const [selectedGroups, setSelectedGroups] = useState<Set<string>>(new Set())
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const handleScan = async () => {
    if (!sourceDir.trim()) {
      setError("Please select a source directory.")
      return
    }
    setLoading(true)
    setError(null)
    setExactPreview(null)
    setSimilarPreview(null)
    setExpandedGroups(new Set())
    try {
      const config = { source_dirs: [sourceDir.trim()], include_patterns: [], exclude_patterns: [] }
      if (tab === "exact") {
        setExactPreview(await duplicateScan(config))
      } else {
        setSimilarPreview(await similarImagesScan({ ...config, hash_size: 8, max_distance: maxDistance, max_images: maxImages, max_pairs: maxPairs }))
      }
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  const browseForSource = async () => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog")
      const selected = await open({ directory: true, multiple: false, title: "Select source directory" })
      if (selected && typeof selected === "string") setSourceDir(selected)
    } catch { /* browser fallback */ }
  }

  const copyPath = (path: string) => {
    navigator.clipboard.writeText(path).catch(() => {})
  }

  const toggleGroup = (digest: string) => {
    setExpandedGroups((prev) => {
      const next = new Set(prev)
      if (next.has(digest)) next.delete(digest)
      else next.add(digest)
      return next
    })
  }

  const toggleGroupSelection = useCallback((groupId: string) => {
    setSelectedGroups(prev => {
      const next = new Set(prev)
      if (next.has(groupId)) { next.delete(groupId) } else { next.add(groupId) }
      return next
    })
  }, [])

  const selectAllGroups = useCallback(() => {
    const active = tab === "exact" ? exactPreview : null
    if (!active?.exact_groups) return
    setSelectedGroups(new Set(active.exact_groups.map(g => g.full_digest)))
  }, [tab, exactPreview])

  const deselectAllGroups = useCallback(() => {
    setSelectedGroups(new Set())
  }, [])

  const totalWastedBytes = useMemo(() => {
    const active = tab === "exact" ? exactPreview : null
    if (!active?.exact_groups) return 0
    let bytes = 0
    for (const g of active.exact_groups) {
      if (selectedGroups.has(g.full_digest) && g.file_size && g.files?.length > 1) {
        bytes += g.file_size * (g.files.length - 1)
      }
    }
    return bytes
  }, [tab, exactPreview, selectedGroups])

  const confirmDelete = useCallback(async () => {
    setShowDeleteConfirm(false)
    const active = tab === "exact" ? exactPreview : null
    if (!active || !sourceDir) return
    setDeleteLoading(true)
    setDeleteResult(null)
    try {
      const decisions: Record<string, string> = {}
      for (const g of active.exact_groups || []) {
        if (selectedGroups.has(g.full_digest) && g.files?.length > 1) {
          decisions[`${g.file_size * g.files.length}:${g.full_digest}`] = g.files[0]
        }
      }
      const result = await duplicatesApply({ source_dirs: [sourceDir], decisions, mode: "delete" })
      setDeleteResult(result as { executed_rows: number; error_rows: number })
      setSelectedGroups(new Set())
      handleScan()
    } catch (e: unknown) {
      setError(String(e))
    } finally {
      setDeleteLoading(false)
    }
  }, [tab, exactPreview, sourceDir, selectedGroups, handleScan])

  const handleDeleteSelected = useCallback(() => {
    if (selectedGroups.size === 0) return
    if (settings.confirm_before_apply) {
      setShowDeleteConfirm(true)
    } else {
      confirmDelete()
    }
  }, [selectedGroups.size, settings.confirm_before_apply, confirmDelete])

  useEffect(() => {
    if (!showDeleteConfirm) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setShowDeleteConfirm(false)
      if (e.key === "Enter") confirmDelete()
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [showDeleteConfirm, confirmDelete])

  const exactFiltered = useMemo(() => {
    if (!exactPreview) return []
    if (!filterPath.trim()) return exactPreview.exact_groups
    const q = filterPath.toLowerCase()
    return exactPreview.exact_groups.filter((g) =>
      g.files.some((f) => f.toLowerCase().includes(q)),
    )
  }, [exactPreview, filterPath])

  // Similar images filtered groups
  const similarFiltered = useMemo(() => {
    if (!similarPreview) return []
    if (!filterPath.trim()) return similarPreview.similar_groups
    const q = filterPath.toLowerCase()
    return similarPreview.similar_groups.filter((g) =>
      g.members.some((m) => m.path.toLowerCase().includes(q)),
    )
  }, [similarPreview, filterPath])

  const exactTotalDupFiles = exactPreview?.exact_groups.reduce((s, g) => s + g.files.length, 0) ?? 0
  const exactWastedCount = exactPreview?.exact_duplicates ?? 0
  const exactWastedBytes = exactPreview?.exact_groups.reduce((s, g) => s + g.file_size * (g.files.length - 1), 0) ?? 0

  return (
    <>
      <PageHeader title="Duplicates" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-4xl space-y-4">
          <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
            Select groups with checkboxes, then click "Delete N Groups" to
            permanently remove duplicates. Deletion cannot be undone.
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Find Duplicates</CardTitle>
              <CardDescription>
                Scan for identical files or visually similar images.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Source folder</label>
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="e.g. C:\Photos"
                    value={sourceDir}
                    onChange={(e) => setSourceDir(e.target.value)}
                    className="flex-1"
                  />
                  <Button variant="outline" size="sm" onClick={browseForSource}>
                    Browse...
                  </Button>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1">
                  Drop a folder here or click Browse
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant={tab === "exact" ? "default" : "outline"}
                  size="sm"
                  onClick={() => { setTab("exact"); setFilterPath(""); setExpandedGroups(new Set()) }}
                >
                  Exact duplicates
                </Button>
                <Button
                  variant={tab === "similar" ? "default" : "outline"}
                  size="sm"
                  onClick={() => { setTab("similar"); setFilterPath(""); setExpandedGroups(new Set()) }}
                >
                  Similar images
                </Button>
              </div>

              {tab === "exact" && (
                <p className="text-xs text-muted-foreground">
                  Finds byte-identical duplicate files using content hashing.
                </p>
              )}

              {tab === "similar" && (
                <div className="space-y-3 rounded-lg border p-3 bg-muted/20">
                  <p className="text-xs text-muted-foreground">
                    Finds visually similar images using perceptual hashing.
                    Higher distance = more matches but more false positives.
                  </p>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-1.5 text-xs">
                      Max distance:
                      <Input
                        type="number"
                        min={0}
                        max={30}
                        value={maxDistance}
                        onChange={(e) => setMaxDistance(Number(e.target.value) || 6)}
                        className="h-7 w-16 text-xs"
                      />
                    </label>
                    <label className="flex items-center gap-1.5 text-xs">
                      Max images:
                      <Input
                        type="number"
                        min={1}
                        max={2000}
                        value={maxImages}
                        onChange={(e) => setMaxImages(Number(e.target.value) || 500)}
                        className="h-7 w-20 text-xs"
                      />
                    </label>
                    <label className="flex items-center gap-1.5 text-xs">
                      Max pairs:
                      <Input
                        type="number"
                        min={1}
                        max={1_000_000}
                        step={10_000}
                        value={maxPairs}
                        onChange={(e) => setMaxPairs(Number(e.target.value) || 150_000)}
                        className="h-7 w-24 text-xs"
                      />
                    </label>
                    <span className="text-xs text-muted-foreground">
                      (pair count = n&times;(n-1)/2, blocked if exceeded)
                    </span>
                  </div>
                </div>
              )}

              {tab === "similar" && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2">
                  <Info className="w-3.5 h-3.5" />
                  Similar image deletion requires perceptual similarity review. Use Exact Duplicates tab for byte-identical copies, or the Review Workbench for similar images.
                </div>
              )}

              <div className="flex items-center gap-3">
                <Button onClick={handleScan} disabled={loading} size="sm">
                  {loading ? "Scanning..." : tab === "exact" ? "Scan for exact duplicates" : "Scan for similar images"}
                </Button>
                {exactPreview && exactPreview.exact_groups.length > 0 && tab === "exact" && (
                  <Button onClick={handleDeleteSelected} disabled={deleteLoading} variant="destructive" size="sm">
                    {deleteLoading ? "Deleting..." : `Delete ${selectedGroups.size} Groups`}
                  </Button>
                )}
                {showDeleteConfirm && (
                  <Card className="border-red-500/50 mt-3 p-3">
                    <p className="text-sm font-medium text-red-400 mb-2">
                      Confirm Deletion
                    </p>
                    <p className="text-xs text-muted-foreground mb-1">
                      This will permanently DELETE {selectedGroups.size} duplicate groups. This action CANNOT be undone. Deleted files are gone forever.
                    </p>
                    {totalWastedBytes > 0 && (
                      <p className="text-xs text-green-400 mb-3">
                        <Trash2 className="w-3 h-3 inline mr-1" />
                        {(totalWastedBytes / 1024 / 1024).toFixed(1)} MB will be freed
                      </p>
                    )}
                    <div className="flex gap-2">
                      <Button onClick={confirmDelete} variant="destructive" size="sm">
                        Yes, delete {selectedGroups.size} groups
                      </Button>
                      <Button onClick={() => setShowDeleteConfirm(false)} variant="ghost" size="sm">
                        Cancel
                      </Button>
                    </div>
                  </Card>
                )}
          {deleteResult && (
            <Card className={deleteResult.error_rows === 0 ? "border-green-500/50" : "border-red-500/50 mt-4"}>
              <CardHeader><CardTitle className={deleteResult.error_rows === 0 ? "text-green-400" : "text-red-400"}>Deletion Result</CardTitle></CardHeader>
              <CardContent className="text-sm">
                <p>Executed: {deleteResult.executed_rows} groups</p>
                {deleteResult.error_rows > 0 && <p className="text-red-400">Errors: {deleteResult.error_rows}</p>}
              </CardContent>
            </Card>
          )}
        </div>
            </CardContent>
          </Card>

          {error && <ErrorBanner message={error} />}

          {loading && (
            <Card>
              <CardContent className="py-8">
                <p className="text-sm text-muted-foreground text-center">Scanning...</p>
              </CardContent>
            </Card>
          )}

          {/* Exact duplicates results */}
          {exactPreview && tab === "exact" && (
            <ExactResults
              preview={exactPreview}
              filteredGroups={exactFiltered}
              totalDupFiles={exactTotalDupFiles}
              wastedCount={exactWastedCount}
              wastedBytes={exactWastedBytes}
              filterPath={filterPath}
              onFilterChange={setFilterPath}
              expandedGroups={expandedGroups}
              onToggleGroup={toggleGroup}
              onCopyPath={copyPath}
              selectedGroups={selectedGroups}
              onToggleGroupSelection={toggleGroupSelection}
              selectAllGroups={selectAllGroups}
              deselectAllGroups={deselectAllGroups}
              totalWastedBytes={totalWastedBytes}
            />
          )}

          {/* Similar images results */}
          {similarPreview && tab === "similar" && (
            <SimilarResults
              preview={similarPreview}
              filteredGroups={similarFiltered}
              filterPath={filterPath}
              onFilterChange={setFilterPath}
              expandedGroups={expandedGroups}
              onToggleGroup={toggleGroup}
              onCopyPath={copyPath}
            />
          )}

          {(exactPreview ?? similarPreview) && (
            <div className="rounded-lg border border-muted px-4 py-3 text-sm text-muted-foreground space-y-1">
              <p>
                Review workflow is not connected yet. Draft decisions exist
                only in memory and are not saved or applied.
              </p>
              <p className="text-xs">
                <a
                  href="/review"
                  className="underline hover:text-foreground"
                  onClick={(e) => {
                    e.preventDefault()
                    window.location.href = "/review"
                  }}
                >
                  Open Review Workbench
                </a>{" "}
                to inspect candidates. Apply, journal, and undo are not
                implemented yet.
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  )
}

// ── Exact duplicates results ──

function ExactResults({
  preview,
  filteredGroups,
  totalDupFiles,
  wastedCount,
  wastedBytes,
  filterPath,
  onFilterChange,
  expandedGroups,
  onToggleGroup,
  onCopyPath,
  selectedGroups,
  onToggleGroupSelection,
  selectAllGroups,
  deselectAllGroups,
  totalWastedBytes,
}: {
  preview: DuplicatesPreviewResponse
  filteredGroups: ExactDuplicateGroup[]
  totalDupFiles: number
  wastedCount: number
  wastedBytes: number
  filterPath: string
  onFilterChange: (v: string) => void
  expandedGroups: Set<string>
  onToggleGroup: (digest: string) => void
  onCopyPath: (path: string) => void
  selectedGroups: Set<string>
  onToggleGroupSelection: (groupId: string) => void
  selectAllGroups: () => void
  deselectAllGroups: () => void
  totalWastedBytes: number
}) {
  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <SummaryCard label="Scanned" value={preview.scanned_files} />
        <SummaryCard label="Groups" value={preview.exact_groups.length} variant={preview.exact_groups.length > 0 ? "default" : "secondary"} />
        <SummaryCard label="In groups" value={totalDupFiles} />
        <SummaryCard label="Wasted copies" value={wastedCount} variant={wastedCount > 0 ? "destructive" : "secondary"} />
        <SummaryCard label="Errors" value={preview.errors} variant={preview.errors > 0 ? "destructive" : "secondary"} />
      </div>

      {wastedBytes > 0 && (
        <div className="rounded-lg border px-4 py-3 text-sm">
          Estimated reclaimable: <span className="font-medium">{formatBytes(wastedBytes)}</span> from {wastedCount} redundant copies
        </div>
      )}

      {preview.exact_groups.length === 0 ? (
        <EmptyState title="No exact duplicates found" description="All scanned files have unique content." />
      ) : (
        <>
          {preview.exact_groups && preview.exact_groups.length > 0 && (
            <div className="flex items-center justify-between mb-2 px-1">
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={selectAllGroups}
                  className="text-xs h-7"
                >
                  <CheckSquare className="w-3.5 h-3.5 mr-1" />
                  Select all ({preview.exact_groups.length})
                </Button>
                {selectedGroups.size > 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={deselectAllGroups}
                    className="text-xs h-7"
                  >
                    <Square className="w-3.5 h-3.5 mr-1" />
                    Deselect all
                  </Button>
                )}
              </div>
              {selectedGroups.size > 0 && (
                <span className="text-xs text-muted-foreground">
                  {selectedGroups.size} selected · {(totalWastedBytes / 1024 / 1024).toFixed(1)} MB wasted
                </span>
              )}
            </div>
          )}
          <GroupsCard
          title={`Duplicate groups (${filteredGroups.length}${filteredGroups.length !== preview.exact_groups.length ? ` of ${preview.exact_groups.length}` : ""})`}
          filterPath={filterPath}
          onFilterChange={onFilterChange}
          filteredCount={filteredGroups.length}
          expandedGroups={expandedGroups}
          onToggleGroup={onToggleGroup}
          onCopyPath={onCopyPath}
          renderGroup={(g) => (
            <div key={(g as ExactDuplicateGroup).full_digest} className={`flex items-start gap-2 ${selectedGroups.has((g as ExactDuplicateGroup).full_digest) ? "ring-1 ring-red-500/30" : ""}`}>
              <input
                type="checkbox"
                checked={selectedGroups.has((g as ExactDuplicateGroup).full_digest)}
                onChange={() => onToggleGroupSelection((g as ExactDuplicateGroup).full_digest)}
                className="mt-1 w-4 h-4 accent-red-500"
              />
              <div className="flex-1">
                <ExactGroupCard group={g as ExactDuplicateGroup} expanded={expandedGroups.has((g as ExactDuplicateGroup).full_digest)} onToggle={() => onToggleGroup((g as ExactDuplicateGroup).full_digest)} onCopyPath={onCopyPath} />
              </div>
            </div>
          )}
          groups={filteredGroups}
        />
        </>
      )}
    </>
  )
}

// ── Similar images results ──

function SimilarResults({
  preview,
  filteredGroups,
  filterPath,
  onFilterChange,
  expandedGroups,
  onToggleGroup,
  onCopyPath,
}: {
  preview: SimilarImagesPreviewResponse
  filteredGroups: SimilarImageGroup[]
  filterPath: string
  onFilterChange: (v: string) => void
  expandedGroups: Set<string>
  onToggleGroup: (digest: string) => void
  onCopyPath: (path: string) => void
}) {
  const totalMembers = preview.similar_groups.reduce((s, g) => s + g.members.length, 0)

  // Guardrail blocked
  if (preview.guardrail?.blocked) {
    return (
      <div className="rounded-lg border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-950 px-4 py-3 text-sm text-yellow-800 dark:text-yellow-200">
        <p className="font-medium">Scan blocked by guardrail</p>
        <p className="text-xs mt-1">{preview.guardrail.reason}</p>
        <p className="text-xs mt-1 text-muted-foreground">
          {preview.guardrail.image_count} images (limit {preview.guardrail.max_images})
          {preview.guardrail.estimated_pairs != null && (
            <> / ~{preview.guardrail.estimated_pairs.toLocaleString()} pairs (limit {preview.guardrail.max_pairs?.toLocaleString()})</>
          )}
          . Increase limits or select a smaller folder.
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <SummaryCard label="Scanned" value={preview.scanned_files} />
        <SummaryCard label="Images" value={preview.image_files} variant="secondary" />
        <SummaryCard label="Groups" value={preview.similar_groups.length} variant={preview.similar_groups.length > 0 ? "default" : "secondary"} />
        <SummaryCard label="Similar pairs" value={preview.similar_pairs} />
        <SummaryCard label="Errors" value={preview.errors} variant={preview.errors > 0 ? "destructive" : "secondary"} />
      </div>

      <div className="grid grid-cols-3 gap-3 text-xs text-muted-foreground">
        <div className="rounded-lg border p-2 text-center">
          {preview.hashed_files} hashed
        </div>
        <div className="rounded-lg border p-2 text-center">
          {preview.exact_hash_pairs} identical hashes
        </div>
        <div className="rounded-lg border p-2 text-center">
          {totalMembers} members in groups
        </div>
      </div>

      {preview.similar_groups.length === 0 ? (
        <EmptyState title="No similar images found" description="No visually similar image pairs detected within the distance threshold." />
      ) : (
        <GroupsCard
          title={`Similar groups (${filteredGroups.length}${filteredGroups.length !== preview.similar_groups.length ? ` of ${preview.similar_groups.length}` : ""})`}
          filterPath={filterPath}
          onFilterChange={onFilterChange}
          filteredCount={filteredGroups.length}
          expandedGroups={expandedGroups}
          onToggleGroup={onToggleGroup}
          onCopyPath={onCopyPath}
          renderGroup={(g) => <SimilarGroupCard group={g as SimilarImageGroup} expanded={expandedGroups.has((g as SimilarImageGroup).anchor_path)} onToggle={() => onToggleGroup((g as SimilarImageGroup).anchor_path)} onCopyPath={onCopyPath} />}
          groups={filteredGroups}
        />
      )}
    </>
  )
}

// ── Shared group list card ──

function GroupsCard({
  title,
  filterPath,
  onFilterChange,
  filteredCount,
  groups,
  expandedGroups: _expandedGroups,
  onToggleGroup: _onToggleGroup,
  onCopyPath: _onCopyPath,
  renderGroup,
}: {
  title: string
  filterPath: string
  onFilterChange: (v: string) => void
  filteredCount: number
  groups: readonly object[]
  expandedGroups: Set<string>
  onToggleGroup: (key: string) => void
  onCopyPath: (path: string) => void
  renderGroup: (group: object) => React.ReactNode
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>Click a group to expand and see all files.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input type="text" placeholder="Filter by file path..." value={filterPath} onChange={(e) => onFilterChange(e.target.value)} className="h-8 text-sm" />
        <div className="overflow-auto max-h-[600px]">
          {filteredCount === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">No groups match the filter.</p>
          ) : (
            <div className="space-y-2">
              {groups.slice(0, 200).map((g, i) => (
                <div key={i}>{renderGroup(g)}</div>
              ))}
            </div>
          )}
        </div>
        {groups.length > 200 && (
          <p className="text-xs text-muted-foreground">Showing first 200 of {groups.length} groups.</p>
        )}
      </CardContent>
    </Card>
  )
}

// ── Exact duplicate group card ──

function ExactGroupCard({
  group,
  expanded,
  onToggle,
  onCopyPath,
}: {
  group: ExactDuplicateGroup
  expanded: boolean
  onToggle: () => void
  onCopyPath: (path: string) => void
}) {
  const wasted = group.file_size * (group.files.length - 1)
  const digestShort = group.full_digest.slice(0, 12)

  return (
    <div className="rounded-lg border">
      <button onClick={onToggle} className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/50 transition-colors">
        <span className="text-xs text-muted-foreground">{expanded ? "▾" : "▸"}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-medium truncate">{group.files[0]?.split(/[\\/]/).pop() ?? "?"}</span>
            <Badge variant="secondary" className="text-xs">{group.files.length} files</Badge>
            {group.same_name && <Badge variant="outline" className="text-xs">same name</Badge>}
            {group.same_suffix && <Badge variant="outline" className="text-xs">same type</Badge>}
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">{formatBytes(group.file_size)} each  /  {wasted > 0 ? formatBytes(wasted) : "0 B"} wasted</p>
        </div>
        <span className="text-xs text-muted-foreground font-mono shrink-0">#{digestShort}</span>
      </button>
      {expanded && (
        <div className="border-t px-3 py-2 space-y-1 bg-muted/20">
          {group.files.map((file) => (
            <div key={file} className="flex items-center gap-2">
              <FileThumbnail path={file} size={64} />
              <span className="truncate font-mono text-xs flex-1">{file}</span>
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={(e) => { e.stopPropagation(); onCopyPath(file) }}>Copy</Button>
            </div>
          ))}
          <div className="flex gap-2 pt-1 text-xs text-muted-foreground font-mono">
            <span>Digest: {group.full_digest}</span>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Similar image group card ──

function SimilarGroupCard({
  group,
  expanded,
  onToggle,
  onCopyPath,
}: {
  group: SimilarImageGroup
  expanded: boolean
  onToggle: () => void
  onCopyPath: (path: string) => void
}) {
  const anchorName = group.anchor_path.split(/[\\/]/).pop() ?? "?"

  return (
    <div className="rounded-lg border">
      <button onClick={onToggle} className="w-full flex items-center gap-3 p-3 text-left hover:bg-muted/50 transition-colors">
        <span className="text-xs text-muted-foreground">{expanded ? "▾" : "▸"}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs font-medium truncate">{anchorName}</span>
            <Badge variant="secondary" className="text-xs">{group.members.length} members</Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            {group.members.filter((m) => m.distance === 0).length} identical  /  {group.members.filter((m) => m.distance > 0).length} similar (max dist {Math.max(...group.members.map((m) => m.distance))})
          </p>
        </div>
      </button>
      {expanded && (
        <div className="border-t px-3 py-2 space-y-1.5 bg-muted/20">
          {group.members.map((m) => (
            <div key={m.path} className="flex items-center gap-2">
              <FileThumbnail path={m.path} size={64} />
              <Badge variant={m.distance === 0 ? "default" : "secondary"} className="text-xs shrink-0">d={m.distance}</Badge>
              <span className="truncate font-mono text-xs flex-1">{m.path}</span>
              {m.width && m.height && <span className="text-xs text-muted-foreground shrink-0">{m.width}x{m.height}</span>}
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={(e) => { e.stopPropagation(); onCopyPath(m.path) }}>Copy</Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function SummaryCard({ label, value, variant = "default" }: { label: string; value: number; variant?: "default" | "secondary" | "destructive" }) {
  const colorClass = variant === "destructive" ? "text-destructive" : variant === "secondary" ? "text-muted-foreground" : "text-foreground"
  return <div className="rounded-lg border p-3 text-center"><p className="text-2xl font-bold tabular-nums">{value}</p><p className={`text-xs ${colorClass}`}>{label}</p></div>
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B"
  const units = ["B", "KB", "MB", "GB", "TB"]
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  return `${(bytes / 1024 ** i).toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}
