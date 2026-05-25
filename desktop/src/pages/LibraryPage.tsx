import { useState, useCallback, useEffect, useRef, useMemo } from "react"
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
import { FolderOpen, Film, Loader2, MoreVertical, Trash2, Pencil, ExternalLink, ChevronLeft, ChevronRight, File, Tag, Check, Play, X, FolderSearch, MapPin, ArrowLeftRight, SlidersHorizontal, Download, Mail, HardDrive } from "lucide-react"
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
import { TagInput } from "@/components/shared/TagInput"
import { TagCloud } from "@/components/shared/TagCloud"
import { Slideshow } from "@/components/shared/Slideshow"
import { SplitView } from "@/components/shared/SplitView"
import { LABEL_COLORS } from "@/components/shared/ColorLabel"
import { PickRejectBar, type FlagState } from "@/components/shared/PickRejectBar"
import { EmailShare } from "@/components/shared/EmailShare"
import { trackRecentlyViewed } from "@/components/shared/RecentFiles"
import { WatchdogIndicator } from "@/components/shared/WatchdogIndicator"

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
  const [thumbQuality, setThumbQuality] = useState<"fast" | "quality">(() => {
    return (localStorage.getItem("thumb_quality") as "fast" | "quality") || "fast"
  })

  const [ratings, setRatings] = useState<Record<string, number>>(() => {
    try { return JSON.parse(localStorage.getItem("library_ratings") || "{}") }
    catch { return {} }
  })

  const [labels, setLabels] = useState<Record<string, string>>(() => {
    try { return JSON.parse(localStorage.getItem("library_labels") || "{}") }
    catch { return {} }
  })

  const [selectedFile, setSelectedFile] = useState<LibraryBrowsePaginatedResult["files"][0] | null>(null)

  const [allTags, setAllTags] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem("library_tags") || "[]") }
    catch { return [] }
  })
  const [fileTags, setFileTags] = useState<Record<string, string[]>>(() => {
    try { return JSON.parse(localStorage.getItem("library_file_tags") || "{}") }
    catch { return {} }
  })
  const [tagFilter, setTagFilter] = useState<string[]>([])

  const [fileFlags, setFileFlags] = useState<Record<string, "pick" | "reject">>(() => {
    try { return JSON.parse(localStorage.getItem("library_flags") || "{}") }
    catch { return {} }
  })
  const [flagFilter, setFlagFilter] = useState<"all" | "pick" | "reject" | "unflagged">("all")
  const [splitViewOpen, setSplitViewOpen] = useState(false)
  const [showEmailShare, setShowEmailShare] = useState(false)
  const [showNetworkHint, setShowNetworkHint] = useState(false)

  const [exifData, setExifData] = useState<Record<string, string | number> | null>(null)

  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [exifFilters, setExifFilters] = useState<{
    camera?: string
    lens?: string
    isoMin?: number
    isoMax?: number
    apertureMin?: string
  }>({})
  const [dragOver, setDragOver] = useState(false)

  useEffect(() => {
    setExifData(null)
  }, [selectedFile])

  const setFlag = useCallback((path: string, state: FlagState) => {
    setFileFlags(prev => {
      const next = { ...prev }
      if (state === "none") {
        delete next[path]
      } else {
        next[path] = state
      }
      localStorage.setItem("library_flags", JSON.stringify(next))
      return next
    })
  }, [])

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

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return
      if (!selectedFile) return
      switch (e.key) {
        case "p": setFlag(selectedFile.path, "pick"); break
        case "x": setFlag(selectedFile.path, "reject"); break
        case "u": setFlag(selectedFile.path, "none"); break
      }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [selectedFile, setFlag])

  const handleOpen = async (path: string, name: string) => {
    setActionLoading(path)
    try {
      await fileOpen(path)
      trackRecentlyViewed(path, name)
    }
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

  const updateFileTags = (path: string, tags: string[]) => {
    setFileTags(prev => {
      const next = { ...prev, [path]: tags }
      localStorage.setItem("library_file_tags", JSON.stringify(next))
      return next
    })
    setAllTags(() => {
      const tagSet = new Set<string>()
      Object.values({ ...fileTags, [path]: tags }).forEach(ts => ts.forEach(t => tagSet.add(t)))
      const newAll = Array.from(tagSet).sort()
      localStorage.setItem("library_tags", JSON.stringify(newAll))
      return newAll
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
    if (selectedPaths.size === sortedFiles.length) {
      setSelectedPaths(new Set())
    } else {
      setSelectedPaths(new Set(sortedFiles.map(f => f.path)))
    }
  }

  const currentFiles = loadedPages.get(page) || []
  const totalPages = data?.total_pages || 1

  const sortedFiles = useMemo(() => {
    let files = currentFiles.filter(f =>
      !filter || f.name.toLowerCase().includes(filter.toLowerCase()) || f.relative.toLowerCase().includes(filter.toLowerCase())
    )
    if (tagFilter.length > 0) {
      files = files.filter(f => {
        const tags = fileTags[f.path] || []
        return tagFilter.some(t => tags.includes(t))
      })
    }
    if (flagFilter !== "all") {
      files = files.filter(f => {
        const flag = fileFlags[f.path]
        if (flagFilter === "pick") return flag === "pick"
        if (flagFilter === "reject") return flag === "reject"
        if (flagFilter === "unflagged") return !flag
        return true
      })
    }
    return files
  }, [currentFiles, filter, tagFilter, fileTags, flagFilter, fileFlags])

  return (
    <div className="p-6 space-y-4"
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragOver(false)
        const files = Array.from(e.dataTransfer.files)
        if (files.length > 0) {
          const path = (files[0] as any).path
          if (path) {
            setRootDir(path)
            browse()
          }
        }
      }}
    >
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
      <div className="flex gap-2 relative">
        <Input
          value={rootDir}
          onChange={e => setRootDir(e.target.value)}
          placeholder={t("Root directory (e.g. organized folder)", "Stammverzeichnis (z.B. organisierter Ordner)")}
          className="text-xs flex-1"
          onKeyDown={e => e.key === "Enter" && browse()}
        />
        <Button variant="ghost" size="sm" className="text-[10px] h-6" onClick={() => setShowNetworkHint(p => !p)}>
          <HardDrive className="h-3 w-3 mr-1" />
          {t("Network", "Netzwerk")}
        </Button>
        {showNetworkHint && (
          <div className="absolute top-full left-0 mt-1 bg-background border rounded p-2 shadow-lg z-10 w-64">
            <p className="text-[10px] font-medium mb-1">{t("Common network paths:", "Häufige Netzwerkpfade:")}</p>
            {[
              "\\\\NAS\\Photos",
              "\\\\SERVER\\Media",
              "Z:\\Photos",
              "/mnt/nas/photos",
              "/Volumes/Media",
            ].map(p => (
              <button key={p} className="block text-[10px] text-left py-0.5 hover:bg-muted rounded px-1 w-full"
                onClick={() => { setRootDir(p); setShowNetworkHint(false) }}>
                <HardDrive className="h-2.5 w-2.5 mr-1 inline text-muted-foreground" />
                {p}
              </button>
            ))}
          </div>
        )}
        <Button onClick={browse} disabled={loading || !rootDir} size="sm">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : t("Browse", "Durchsuchen")}
        </Button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {data && (
        <WatchdogIndicator rootDir={rootDir} onRescan={browse} />
      )}

      {/* Toolbar */}
      {data && (
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Badge variant="outline">{data.file_count} {t("files", "Dateien")}</Badge>
            {selectMode && (
              <Button variant="outline" size="sm" onClick={selectAll}>
                {selectedPaths.size === sortedFiles.length ? t("Deselect all", "Alle abwählen") : t("Select all", "Alle auswählen")}
              </Button>
            )}
            <Input
              value={filter}
              onChange={e => { setFilter(e.target.value); setPage(0) }}
              placeholder={t("Filter by name...", "Nach Name filtern...")}
              className="text-xs w-48"
            />
            {allTags.length > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground">{t("Filter by tag:", "Nach Tag filtern:")}</span>
                <TagCloud
                  tags={allTags}
                  selectedTags={tagFilter}
                  onToggle={(tag) => {
                    setTagFilter(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag])
                    setPage(0)
                  }}
                />
              </div>
            )}
            <div className="flex items-center gap-1 border rounded p-0.5">
              {(["all", "pick", "reject", "unflagged"] as const).map(f => (
                <button
                  key={f}
                  onClick={() => { setFlagFilter(f); setPage(0) }}
                  className={`text-[10px] px-1.5 py-0.5 rounded transition-colors ${
                    flagFilter === f ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {f === "all" ? t("All", "Alle") :
                   f === "pick" ? t("Picks", "Auswahl") :
                   f === "reject" ? t("Rejects", "Abgelehnt") :
                   t("Unflagged", "Unmarkiert")}
                </button>
              ))}
            </div>
            {(tagFilter.length > 0 || flagFilter !== "all") && (
              <Button variant="outline" size="sm" onClick={() => {
                const name = prompt(t("Collection name:", "Sammlungsname:"))
                if (!name) return
                const collections = JSON.parse(localStorage.getItem("smart_collections") || "[]")
                collections.push({
                  id: Date.now().toString(),
                  name,
                  rules: { tags: tagFilter.length > 0 ? tagFilter : undefined, flagState: flagFilter !== "all" ? (flagFilter === "pick" ? "pick" : flagFilter === "reject" ? "reject" : undefined) : undefined, dateFrom: data?.applied_filters?.date_from || undefined, dateTo: data?.applied_filters?.date_to || undefined },
                  createdAt: new Date().toISOString()
                })
                localStorage.setItem("smart_collections", JSON.stringify(collections))
              }}>
                <FolderSearch className="h-3 w-3 mr-1" /> {t("Save as Collection", "Als Sammlung speichern")}
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={() => setShowAdvancedFilters(f => !f)}
              className="text-[10px]">
              <SlidersHorizontal className="h-3 w-3 mr-1" />
              {showAdvancedFilters ? t("Hide filters", "Filter verbergen") : t("Advanced filters", "Erweiterte Filter")}
            </Button>
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
            {selectMode && selectedPaths.size >= 2 && (
              <Button variant="outline" size="sm" onClick={() => setSplitViewOpen(true)}>
                <ArrowLeftRight className="h-3 w-3 mr-1" /> {t("Compare", "Vergleichen")}
              </Button>
            )}
            <span className="text-xs text-muted-foreground">{t("Per page:", "Pro Seite:")}</span>
            <button onClick={() => {
              const next = thumbQuality === "fast" ? "quality" : "fast"
              setThumbQuality(next)
              localStorage.setItem("thumb_quality", next)
            }} className="text-[10px] px-1.5 py-0.5 rounded border bg-muted/50"
              title={t("Toggle thumbnail quality", "Vorschaubild-Qualität umschalten")}>
              {thumbQuality === "fast" ? "⚡" : "🖼️"}
            </button>
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

      {showAdvancedFilters && data && (
        <div className="flex flex-wrap gap-2 p-2 border rounded bg-muted/20">
          <input placeholder={t("Camera model...", "Kamera-Modell...")}
            className="text-[10px] border rounded px-2 py-1 w-32 bg-background"
            value={exifFilters.camera || ""}
            onChange={e => setExifFilters(prev => ({...prev, camera: e.target.value || undefined}))} />
          <input placeholder={t("Lens...", "Objektiv...")}
            className="text-[10px] border rounded px-2 py-1 w-32 bg-background"
            value={exifFilters.lens || ""}
            onChange={e => setExifFilters(prev => ({...prev, lens: e.target.value || undefined}))} />
          <input placeholder={t("ISO min", "ISO min")} type="number"
            className="text-[10px] border rounded px-2 py-1 w-20 bg-background"
            onChange={e => setExifFilters(prev => ({...prev, isoMin: e.target.value ? Number(e.target.value) : undefined}))} />
          <input placeholder={t("ISO max", "ISO max")} type="number"
            className="text-[10px] border rounded px-2 py-1 w-20 bg-background"
            onChange={e => setExifFilters(prev => ({...prev, isoMax: e.target.value ? Number(e.target.value) : undefined}))} />
          {(exifFilters.camera || exifFilters.lens || exifFilters.isoMin || exifFilters.isoMax) && (
            <Button variant="ghost" size="sm" className="text-[10px]"
              onClick={() => setExifFilters({})}>
              {t("Clear", "Löschen")}
            </Button>
          )}
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
          {sortedFiles.map((f) => (
            <Card
              key={f.path}
              className={`overflow-hidden hover:border-primary/30 transition-colors group relative ${selectedPaths.has(f.path) ? "ring-2 ring-primary" : ""}`}
              role="button"
              tabIndex={0}
              onKeyDown={e => e.key === "Enter" && handleOpen(f.path, f.name)}
              onClick={selectMode ? () => toggleSelect(f.path) : () => setSelectedFile(f)}
              onDoubleClick={() => handleOpen(f.path, f.name)}
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
                {!selectMode && fileFlags[f.path] && (
                  <div className={`absolute top-1 left-1 w-5 h-5 rounded-full flex items-center justify-center text-[10px] z-20 ${
                    fileFlags[f.path] === "pick" ? "bg-green-500 text-white" : "bg-red-500 text-white"
                  }`}>
                    {fileFlags[f.path] === "pick" ? "✓" : "✕"}
                  </div>
                )}
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
                    onClick={(e) => { e.stopPropagation(); handleOpen(f.path, f.name) }}
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
                      <DropdownMenuItem onClick={() => handleOpen(f.path, f.name)} disabled={actionLoading === f.path}>
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
                      <DropdownMenuSeparator />
                      <div className="px-2 py-1">
                        <PickRejectBar
                          flagState={fileFlags[f.path] || "none"}
                          onFlag={(state) => setFlag(f.path, state)}
                          compact
                        />
                      </div>
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
                {/* Tags */}
                <div className="mt-1">
                  <TagInput
                    tags={fileTags[f.path] || []}
                    onChange={(tags) => updateFileTags(f.path, tags)}
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Detail panel */}
      {selectedFile && (
        <div className="fixed inset-y-0 right-0 w-80 bg-background border-l shadow-lg z-50 overflow-y-auto p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-sm">{t("File details", "Datei-Details")}</h3>
            <button
              onClick={() => setSelectedFile(null)}
              className="h-6 w-6 flex items-center justify-center rounded hover:bg-muted"
              aria-label={t("Close", "Schließen")}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <span className="text-muted-foreground">{t("Name", "Name")}</span>
            <span className="truncate">{selectedFile.name}</span>
            <span className="text-muted-foreground">{t("Type", "Typ")}</span>
            <span className="truncate">{selectedFile.category || selectedFile.suffix}</span>
            <span className="text-muted-foreground">{t("Size", "Größe")}</span>
            <span>{formatSize(selectedFile.size)}</span>
            <span className="text-muted-foreground">{t("Path", "Pfad")}</span>
            <span className="truncate text-[10px]" title={selectedFile.path}>{selectedFile.relative}</span>
          </div>
          <div className="flex items-center justify-between mt-3 pt-3 border-t">
            <span className="text-[10px] text-muted-foreground">{t("Flag", "Markierung")}</span>
            <PickRejectBar
              flagState={fileFlags[selectedFile.path] || "none"}
              onFlag={(state) => setFlag(selectedFile.path, state)}
              compact
            />
          </div>
          <div className="mt-3 pt-3 border-t">
            <span className="text-[10px] text-muted-foreground">{t("Tags", "Tags")}</span>
            <div className="mt-1">
              <TagInput
                tags={fileTags[selectedFile.path] || []}
                onChange={(tags) => updateFileTags(selectedFile.path, tags)}
              />
            </div>
          </div>
          {exifData?.gps_latitude != null && exifData.gps_longitude != null && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-[10px] text-muted-foreground">{t("GPS", "GPS")}</span>
              <div className="mt-1 text-[10px] text-muted-foreground">
                {String(exifData.gps_latitude)}, {String(exifData.gps_longitude)}
              </div>
              <div className="mt-2 rounded overflow-hidden border">
                <img
                  src={`https://staticmap.openstreetmap.de/staticmap.php?center=${encodeURIComponent(String(exifData.gps_latitude))},${encodeURIComponent(String(exifData.gps_longitude))}&zoom=12&size=400x200&markers=${encodeURIComponent(String(exifData.gps_latitude))},${encodeURIComponent(String(exifData.gps_longitude))},red-pushpin`}
                  alt={t("Map location", "Kartenposition")}
                  className="w-full h-32 object-cover"
                />
              </div>
              <div className="mt-2">
                <Button variant="outline" size="sm" onClick={() => {
                  const lat = String(exifData.gps_latitude).replace(/deg|'|"/g, "").trim()
                  const lon = String(exifData.gps_longitude).replace(/deg|'|"/g, "").trim()
                  window.open(`https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}&zoom=15`, "_blank")
                }}>
                  <MapPin className="h-3 w-3 mr-1" />
                  {t("View on map", "Auf Karte zeigen")}
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Batch action bar */}
      {selectMode && selectedPaths.size > 0 && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-background border shadow-lg rounded-lg px-4 py-2 flex items-center gap-3 z-40">
          <span className="text-sm font-medium">{selectedPaths.size} {t("selected", "ausgewählt")}</span>

          <div className="flex items-center gap-1">
            <input
              placeholder={t("Add tag to all...", "Tag für alle...")}
              className="text-xs border rounded px-2 py-1 w-32 bg-background"
              onKeyDown={(e) => {
                if (e.key === "Enter" && e.currentTarget.value.trim()) {
                  const tag = e.currentTarget.value.trim().toLowerCase()
                  const newFileTags = { ...fileTags }
                  selectedPaths.forEach(path => {
                    const existing = newFileTags[path] || []
                    if (!existing.includes(tag)) {
                      newFileTags[path] = [...existing, tag]
                    }
                  })
                  setFileTags(newFileTags)
                  localStorage.setItem("library_file_tags", JSON.stringify(newFileTags))
                  const tagSet = new Set<string>()
                  Object.values(newFileTags).forEach(ts => ts.forEach(t => tagSet.add(t)))
                  setAllTags(Array.from(tagSet).sort())
                  localStorage.setItem("library_tags", JSON.stringify(Array.from(tagSet).sort()))
                  e.currentTarget.value = ""
                }
              }}
            />
          </div>

          <Button size="sm" variant="outline" onClick={() => {
            const newFlags = { ...fileFlags }
            selectedPaths.forEach(path => { newFlags[path] = "pick" })
            setFileFlags(newFlags)
            localStorage.setItem("library_flags", JSON.stringify(newFlags))
          }}>
            <Check className="h-3 w-3 mr-1 text-green-500" /> {t("Pick all", "Alle wählen")}
          </Button>

          <Button size="sm" variant="outline" onClick={() => {
            const newFlags = { ...fileFlags }
            selectedPaths.forEach(path => { newFlags[path] = "reject" })
            setFileFlags(newFlags)
            localStorage.setItem("library_flags", JSON.stringify(newFlags))
          }}>
            <X className="h-3 w-3 mr-1 text-red-500" /> {t("Reject all", "Alle ablehnen")}
          </Button>

          <Button size="sm" variant="outline" onClick={() => handleReveal(Array.from(selectedPaths)[0])}>
            <FolderOpen className="h-3 w-3 mr-1" /> {t("Reveal", "Zeigen")}
          </Button>

          <Button size="sm" variant="outline" onClick={() => setShowEmailShare(true)}>
            <Mail className="h-3 w-3 mr-1" /> {t("Share", "Teilen")}
          </Button>

          <Button size="sm" variant="outline" onClick={() => setSelectedPaths(new Set())}>
            {t("Clear", "Löschen")}
          </Button>
        </div>
      )}

      {/* Empty states */}
      {!loading && data && sortedFiles.length === 0 && (
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

      {/* Split View */}
      {splitViewOpen && (
        <SplitView
          files={currentFiles.filter(f => selectedPaths.has(f.path)).map(f => ({ path: f.path, name: f.name }))}
          onClose={() => setSplitViewOpen(false)}
        />
      )}

      {/* Email Share modal */}
      {showEmailShare && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowEmailShare(false)}>
          <div onClick={e => e.stopPropagation()}>
            <EmailShare selectedPaths={Array.from(selectedPaths)} onClose={() => setShowEmailShare(false)} />
          </div>
        </div>
      )}

      {/* Drag & Drop overlay */}
      {dragOver && (
        <div className="fixed inset-0 z-50 bg-primary/10 border-2 border-dashed border-primary flex items-center justify-center pointer-events-none">
          <div className="bg-background rounded-xl p-6 shadow-lg text-center">
            <Download className="h-10 w-10 text-primary mx-auto mb-2" />
            <p className="text-lg font-semibold">{t("Drop folder here", "Ordner hier ablegen")}</p>
            <p className="text-sm text-muted-foreground">{t("The folder will be set as library root", "Der Ordner wird als Bibliotheks-Stamm festgelegt")}</p>
          </div>
        </div>
      )}
    </div>
  )
}
