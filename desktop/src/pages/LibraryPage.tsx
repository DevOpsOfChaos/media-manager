import { useState, useCallback, useEffect, useRef } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { EmptyState } from "@/components/shared/EmptyState"
import { libraryBrowsePaginated, fileOpen, fileReveal, fileDelete, fileRename, type LibraryBrowsePaginatedResult } from "@/lib/tauri-bridge"
import { convertFileSrc } from "@tauri-apps/api/core"
import { FolderOpen, Film, Loader2, MoreVertical, Trash2, Pencil, ExternalLink, ChevronLeft, ChevronRight, File, Tag, Check, Play } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu"
import { StarRating } from "@/components/shared/StarRating"
import { Slideshow } from "@/components/shared/Slideshow"
import { LABEL_COLORS } from "@/components/shared/ColorLabel"

const PAGE_SIZE_OPTIONS = [12, 24, 48, 96]

const SUFFIX_COLORS: Record<string, string> = {
  ".jpg": "bg-blue-500/10 text-blue-400", ".jpeg": "bg-blue-500/10 text-blue-400",
  ".png": "bg-green-500/10 text-green-400", ".mp4": "bg-red-500/10 text-red-400",
  ".mov": "bg-red-500/10 text-red-400", ".cr2": "bg-yellow-500/10 text-yellow-400",
  ".cr3": "bg-yellow-500/10 text-yellow-400", ".nef": "bg-yellow-500/10 text-yellow-400",
  ".arw": "bg-yellow-500/10 text-yellow-400", ".dng": "bg-yellow-500/10 text-yellow-400",
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

function isImageFile(suffix: string): boolean {
  return [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".heic"].includes(suffix)
}

function isVideoFile(suffix: string): boolean {
  return [".mp4", ".mov", ".avi", ".mkv", ".webm"].includes(suffix)
}

export default function LibraryPage() {
  const t = useT()
  const [rootDir, setRootDir] = useState(() => localStorage.getItem("library_root") || localStorage.getItem("default_source_dir") || "")
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<LibraryBrowsePaginatedResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState("")
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(48)
  const [loadedPages, setLoadedPages] = useState<Map<number, LibraryBrowsePaginatedResult["files"]>>(new Map())
  const [deleteDialog, setDeleteDialog] = useState<{ path: string; name: string } | null>(null)
  const [renameDialog, setRenameDialog] = useState<{ path: string; name: string } | null>(null)
  const [renameValue, setRenameValue] = useState("")
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const preloadQueue = useRef<Set<number>>(new Set())
  const [slideshowOpen, setSlideshowOpen] = useState(false)
  const [selectMode, setSelectMode] = useState(false)
  const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set())

  const [ratings, setRatings] = useState<Record<string, number>>(() => {
    try { return JSON.parse(localStorage.getItem("library_ratings") || "{}") }
    catch { return {} }
  })

  const [labels, setLabels] = useState<Record<string, string>>(() => {
    try { return JSON.parse(localStorage.getItem("library_labels") || "{}") }
    catch { return {} }
  })

  const loadPageData = useCallback(async (pageNum: number) => {
    if (!rootDir) return
    if (preloadQueue.current.has(pageNum)) return

    preloadQueue.current.add(pageNum)
    try {
      const r = await libraryBrowsePaginated({
        root_dir: rootDir,
        page: pageNum,
        page_size: pageSize,
      })
      setLoadedPages(prev => {
        const next = new Map(prev)
        next.set(pageNum, r.files)
        return next
      })
      if (pageNum === page) {
        setData(r)
      }
    } catch (e) {
      console.error(`Failed to load page ${pageNum}:`, e)
    } finally {
      preloadQueue.current.delete(pageNum)
    }
  }, [rootDir, pageSize, page])

  const browse = useCallback(async () => {
    if (!rootDir) return
    setLoading(true); setError(null); setPage(0); setLoadedPages(new Map())
    localStorage.setItem("library_root", rootDir)
    try {
      await loadPageData(0)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }, [rootDir, loadPageData])

  useEffect(() => {
    if (!data || loading) return
    loadPageData(page)
    if (page + 1 < (data.total_pages || 1)) {
      const t1 = setTimeout(() => loadPageData(page + 1), 200)
      return () => clearTimeout(t1)
    }
    if (page - 1 >= 0) {
      const t2 = setTimeout(() => loadPageData(page - 1), 400)
      return () => clearTimeout(t2)
    }
  }, [page, data?.total_pages, loadPageData, loading, data])

  useEffect(() => {
    setSelectedPaths(new Set())
  }, [page])

  const handleOpen = async (path: string) => {
    setActionLoading(path)
    try { await fileOpen(path) }
    catch (e) { setError(String(e)) }
    finally { setActionLoading(null) }
  }

  const handleReveal = async (path: string) => {
    try { await fileReveal(path) }
    catch (e) { setError(String(e)) }
  }

  const handleDeleteConfirm = async () => {
    if (!deleteDialog) return
    try {
      await fileDelete(deleteDialog.path)
      setDeleteDialog(null)
      const next = new Map(loadedPages)
      next.delete(page)
      setLoadedPages(next)
      loadPageData(page)
    } catch (e) { setError(String(e)) }
  }

  const handleSetLabel = (filePath: string, color: string) => {
    setLabels(prev => {
      const next = { ...prev, [filePath]: color }
      localStorage.setItem("library_labels", JSON.stringify(next))
      return next
    })
  }

  const handleRenameConfirm = async () => {
    if (!renameDialog || !renameValue.trim()) return
    try {
      await fileRename(renameDialog.path, renameValue.trim())
      setRenameDialog(null)
      const next = new Map(loadedPages)
      next.delete(page)
      setLoadedPages(next)
      loadPageData(page)
    } catch (e) { setError(String(e)) }
  }

  const toggleSelect = (path: string) => {
    setSelectedPaths(prev => {
      const next = new Set(prev)
      if (next.has(path)) next.delete(path)
      else next.add(path)
      return next
    })
  }

  const selectAll = () => {
    if (selectedPaths.size === currentFiles.length) {
      setSelectedPaths(new Set())
    } else {
      setSelectedPaths(new Set(currentFiles.map(f => f.path)))
    }
  }

  const currentFiles = loadedPages.get(page) || []
  const totalPages = data?.total_pages || 1

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <FolderOpen className="w-6 h-6 text-primary" />
        <div className="flex-1">
          <h1 className="text-xl font-bold">{t("Library", "Bibliothek")}</h1>
          <p className="text-sm text-muted-foreground">
            {t("Browse your media files with actions.", "Medien durchsuchen mit Aktionen.")}
          </p>
        </div>
      </div>

      {/* Search bar */}
      <div className="flex gap-2">
        <Input
          value={rootDir}
          onChange={e => setRootDir(e.target.value)}
          placeholder={t("Root directory (e.g. organized folder)", "Stammverzeichnis (z.B. organisierter Ordner)")}
          className="text-xs flex-1"
          onKeyDown={e => e.key === "Enter" && browse()}
        />
        <Button onClick={browse} disabled={loading || !rootDir} size="sm">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : t("Browse", "Durchsuchen")}
        </Button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {/* Toolbar */}
      {data && (
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Badge variant="outline">{data.file_count} {t("files", "Dateien")}</Badge>
            {selectMode && (
              <Button variant="outline" size="sm" onClick={selectAll}>
                {selectedPaths.size === currentFiles.length ? t("Deselect all", "Alle abwählen") : t("Select all", "Alle auswählen")}
              </Button>
            )}
            <Input
              value={filter}
              onChange={e => { setFilter(e.target.value); setPage(0) }}
              placeholder={t("Filter by name...", "Nach Name filtern...")}
              className="text-xs w-48"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setSlideshowOpen(true)}
              disabled={currentFiles.length === 0}>
              <Play className="h-3 w-3 mr-1" /> {t("Slideshow", "Diashow")}
            </Button>
            <Button variant={selectMode ? "default" : "outline"} size="sm"
              onClick={() => { setSelectMode(!selectMode); setSelectedPaths(new Set()) }}>
              {selectMode ? t("Done", "Fertig") : t("Select", "Auswählen")}
            </Button>
            <span className="text-xs text-muted-foreground">{t("Per page:", "Pro Seite:")}</span>
            <select
              value={pageSize}
              onChange={e => {
                const newSize = Number(e.target.value)
                setPageSize(newSize)
                setPage(0)
                setLoadedPages(new Map())
                loadPageData(0)
              }}
              className="text-xs border rounded px-2 py-1 bg-background"
            >
              {PAGE_SIZE_OPTIONS.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-2">
          {Array.from({ length: pageSize }).map((_, i) => (
            <Card key={i} className="overflow-hidden">
              <Skeleton className="aspect-square w-full" />
              <CardContent className="p-2 space-y-1">
                <Skeleton className="h-3 w-3/4" />
                <Skeleton className="h-2 w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* File grid */}
      {!loading && data && currentFiles.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-2">
          {currentFiles.filter(f =>
            !filter || f.name.toLowerCase().includes(filter.toLowerCase()) || f.relative.toLowerCase().includes(filter.toLowerCase())
          ).map((f) => (
            <Card
              key={f.path}
              className={`overflow-hidden hover:border-primary/30 transition-colors group relative ${selectedPaths.has(f.path) ? "ring-2 ring-primary" : ""}`}
              role="button"
              tabIndex={0}
              onKeyDown={e => e.key === "Enter" && handleOpen(f.path)}
              onClick={selectMode ? () => toggleSelect(f.path) : undefined}
              onDoubleClick={() => handleOpen(f.path)}
            >
              {/* Select checkbox */}
              {selectMode && (
                <div
                  className={`absolute top-1 left-1 z-20 h-5 w-5 rounded border-2 flex items-center justify-center cursor-pointer transition-colors ${
                    selectedPaths.has(f.path) ? "bg-primary border-primary" : "border-primary/50 bg-background/80"
                  }`}
                  onClick={(e) => { e.stopPropagation(); toggleSelect(f.path) }}
                >
                  {selectedPaths.has(f.path) && <Check className="h-3 w-3 text-primary-foreground" />}
                </div>
              )}
              {/* Color label dot */}
              {labels[f.path] && labels[f.path] !== "none" && (
                <div className={`absolute top-1 right-1 h-2 w-2 rounded-full bg-${labels[f.path]}-500 z-10`} />
              )}

              {/* Thumbnail */}
              <div className="aspect-square bg-muted relative overflow-hidden">
                {isImageFile(f.suffix) ? (
                  <img
                    src={convertFileSrc(f.path)}
                    alt={f.name}
                    className="w-full h-full object-cover"
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none"
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    {isVideoFile(f.suffix) ? (
                      <Film className="w-10 h-10 text-muted-foreground/40" />
                    ) : (
                      <File className="w-10 h-10 text-muted-foreground/40" />
                    )}
                  </div>
                )}
                {/* Action overlay on hover */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <Button
                    size="sm"
                    variant="secondary"
                    className="h-7 text-xs"
                    onClick={(e) => { e.stopPropagation(); handleOpen(f.path) }}
                  >
                    {t("Open", "Öffnen")}
                  </Button>
                </div>
              </div>

              {/* File info */}
              <CardContent className="p-2">
                <div className="flex items-start justify-between gap-1">
                  <p className="text-[11px] font-medium truncate flex-1" title={f.name}>{f.name}</p>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <button
                        className="h-5 w-5 flex items-center justify-center rounded hover:bg-muted opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={e => e.stopPropagation()}
                        aria-label={t("Actions", "Aktionen")}
                      >
                        <MoreVertical className="h-3 w-3" />
                      </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-40">
                      <DropdownMenuItem onClick={() => handleOpen(f.path)} disabled={actionLoading === f.path}>
                        <ExternalLink className="h-3.5 w-3.5 mr-2" />
                        {t("Open", "Öffnen")}
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => handleReveal(f.path)}>
                        <FolderOpen className="h-3.5 w-3.5 mr-2" />
                        {t("Show in folder", "Im Ordner zeigen")}
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuSub>
                        <DropdownMenuSubTrigger>
                          <Tag className="h-3.5 w-3.5 mr-2" />
                          {t("Color label", "Farb-Label")}
                        </DropdownMenuSubTrigger>
                        <DropdownMenuSubContent>
                          {LABEL_COLORS.map(c => (
                            <DropdownMenuItem key={c.key} onClick={() => handleSetLabel(f.path, c.key)}>
                              <div className={`h-3 w-3 rounded-full ${c.bg} mr-2`} />
                              {t(c.label, c.label)}
                              {labels[f.path] === c.key && <Check className="h-3 w-3 ml-auto" />}
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuSubContent>
                      </DropdownMenuSub>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={() => { setRenameDialog({ path: f.path, name: f.name }); setRenameValue(f.name) }}>
                        <Pencil className="h-3.5 w-3.5 mr-2" />
                        {t("Rename", "Umbenennen")}
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => setDeleteDialog({ path: f.path, name: f.name })}
                        className="text-red-500"
                      >
                        <Trash2 className="h-3.5 w-3.5 mr-2" />
                        {t("Delete", "Löschen")}
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <Badge className={`text-[9px] px-1 py-0 ${SUFFIX_COLORS[f.suffix] || "bg-muted text-muted-foreground"}`}>
                    {f.suffix}
                  </Badge>
                  <span className="text-[10px] text-muted-foreground">{formatSize(f.size)}</span>
                </div>
                {/* Star rating */}
                <div className="mt-0.5">
                  <StarRating
                    value={ratings[f.path] || 0}
                    onChange={(v) => {
                      setRatings(prev => {
                        const next = { ...prev, [f.path]: v }
                        localStorage.setItem("library_ratings", JSON.stringify(next))
                        return next
                      })
                    }}
                    size="sm"
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Batch action bar */}
      {selectMode && selectedPaths.size > 0 && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-background border shadow-lg rounded-lg px-4 py-2 flex items-center gap-3 z-40">
          <span className="text-sm font-medium">{selectedPaths.size} {t("selected", "ausgewählt")}</span>
          <Button size="sm" variant="outline" onClick={() => selectedPaths.forEach(p => handleReveal(p))}>
            <FolderOpen className="h-3 w-3 mr-1" /> {t("Reveal all", "Alle zeigen")}
          </Button>
          <Button size="sm" variant="outline" onClick={() => setSelectedPaths(new Set())}>
            {t("Clear", "Löschen")}
          </Button>
        </div>
      )}

      {/* Empty states */}
      {!loading && data && currentFiles.length === 0 && (
        <EmptyState
          title={filter ? t("No matches", "Keine Treffer") : t("No files found", "Keine Dateien gefunden")}
          description={filter ? t("Try a different filter.", "Anderen Filter versuchen.") : t("The directory is empty.", "Das Verzeichnis ist leer.")}
        />
      )}

      {!data && !loading && (
        <EmptyState
          title={t("No directory selected", "Kein Verzeichnis ausgewählt")}
          description={t("Enter a root directory and click Browse.", "Stammverzeichnis eingeben und Durchsuchen klicken.")}
        />
      )}

      {/* Pagination controls */}
      {data && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-xs text-muted-foreground min-w-[80px] text-center">
            {t(`Page ${page + 1} of ${totalPages}`, `Seite ${page + 1} von ${totalPages}`)}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}

      {/* Delete confirmation dialog */}
      <Dialog open={!!deleteDialog} onOpenChange={() => setDeleteDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("Delete file?", "Datei löschen?")}</DialogTitle>
            <DialogDescription>
              {t(`Move "${deleteDialog?.name}" to trash? This can be undone from your system trash.`,
                 `"${deleteDialog?.name}" in den Papierkorb verschieben? Kann aus dem Papierkorb wiederhergestellt werden.`)}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialog(null)}>
              {t("Cancel", "Abbrechen")}
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm}>
              {t("Move to trash", "In Papierkorb")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rename dialog */}
      <Dialog open={!!renameDialog} onOpenChange={() => setRenameDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("Rename file", "Datei umbenennen")}</DialogTitle>
            <DialogDescription>
              {t("Enter a new name for this file.", "Neuen Namen für diese Datei eingeben.")}
            </DialogDescription>
          </DialogHeader>
          <Input
            value={renameValue}
            onChange={e => setRenameValue(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleRenameConfirm()}
            placeholder={t("New filename", "Neuer Dateiname")}
            autoFocus
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameDialog(null)}>
              {t("Cancel", "Abbrechen")}
            </Button>
            <Button onClick={handleRenameConfirm} disabled={!renameValue.trim() || renameValue === renameDialog?.name}>
              {t("Rename", "Umbenennen")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Slideshow */}
      {slideshowOpen && (
        <Slideshow
          files={currentFiles.map(f => ({ path: f.path, name: f.name }))}
          onClose={() => setSlideshowOpen(false)}
        />
      )}
    </div>
  )
}
