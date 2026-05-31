import { useState, useCallback, useEffect, useRef, useMemo, memo, lazy, Suspense } from "react"
import { useNavigate } from "react-router-dom"
import { convertFileSrc } from "@tauri-apps/api/core"
import { useT } from "@/lib/i18n"
import { useFirstRunHint } from "@/lib/use-first-run-hint"
import { toast } from "@/lib/toast"
import { PageHeader } from "@/components/layout/PageHeader"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { EmptyState } from "@/components/shared/EmptyState"
import { Skeleton } from "@/components/ui/skeleton"
import { fileOpen, fileReveal, fileDelete, fileRename, fileExport, enrichFile, magicDetect, healthCheckFile, type EnrichedFile, type LibraryBrowsePaginatedResult, type MagicDetectResult, type FileHealthResult } from "@/lib/tauri-bridge"
import { cachedCall, dedupedCall } from "@/lib/api-cache"

import { FolderOpen, FolderSync, Loader2, MoreVertical, Trash2, Pencil, ExternalLink, ChevronLeft, ChevronRight, Tag, Check, Play, X, FolderSearch, MapPin, ArrowLeftRight, SlidersHorizontal, Download, Mail, HardDrive, Film, Music, File } from "lucide-react"
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
import { SplitView } from "@/components/shared/SplitView"

const Slideshow = lazy(() => import("@/components/shared/Slideshow").then(m => ({ default: m.Slideshow })))
import { LABEL_COLORS } from "@/components/shared/ColorLabel"

const LABEL_CLASS_MAP: Record<string, string> = {
  red: "bg-red-500",
  yellow: "bg-yellow-500",
  green: "bg-green-500",
  blue: "bg-blue-500",
  purple: "bg-purple-500",
}
import { PickRejectBar, type FlagState } from "@/components/shared/PickRejectBar"
import { EmailShare } from "@/components/shared/EmailShare"
import { trackRecentlyViewed } from "@/components/shared/RecentFiles"
import { WatchdogIndicator } from "@/components/shared/WatchdogIndicator"
import { MetadataScoreBadge } from "@/components/shared/MetadataScoreBadge"
import { HealthIndicator } from "@/components/shared/HealthIndicator"
import { ExtensionMismatchWarning } from "@/components/shared/ExtensionMismatchWarning"


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

function isVideoFile(suffix: string): boolean {
  return [".mp4", ".mov", ".avi", ".mkv", ".webm"].includes(suffix)
}

function isImageFile(suffix: string): boolean {
  return !isVideoFile(suffix) && !isAudioFile(suffix)
}

function isAudioFile(suffix: string): boolean {
  return [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"].includes(suffix)
}

type FileItem = LibraryBrowsePaginatedResult["files"][0]

const FileCard = memo(function FileCard({
  f,
  isSelected,
  isCrossDupe,
  label,
  flag,
  rating,
  tags,
  isActionLoading,
  selectMode,
  exifData,
  onOpen,
  onReveal,
  onSetLabel,
  onFlag,
  onDeleteDialog,
  onRenameDialog,
  onToggleSelect,
  onSelectFile,
  onUpdateTags,
  onRatingChange,
}: {
  f: FileItem
  isSelected: boolean
  isCrossDupe: boolean
  label: string | undefined
  flag: "pick" | "reject" | undefined
  rating: number
  tags: string[]
  isActionLoading: boolean
  selectMode: boolean
  exifData: EnrichedFile | null
  onOpen: (path: string, name: string) => void
  onReveal: (path: string) => void
  onSetLabel: (path: string, color: string) => void
  onFlag: (path: string, state: FlagState) => void
  onDeleteDialog: (item: { path: string; name: string }) => void
  onRenameDialog: (item: { path: string; name: string }) => void
  onToggleSelect: (path: string) => void
  onSelectFile: (f: FileItem) => void
  onUpdateTags: (path: string, tags: string[]) => void
  onRatingChange: (path: string, value: number) => void
}) {
  const t = useT()

  return (
    <Card
      className={`overflow-hidden hover:border-primary/30 transition-colors group relative cursor-pointer ${isSelected ? "ring-2 ring-primary" : ""} ${isCrossDupe ? "ring-2 ring-yellow-500/50" : ""}`}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === "Enter" && onOpen(f.path, f.name)}
      onClick={selectMode ? () => onToggleSelect(f.path) : () => onSelectFile(f)}
      onDoubleClick={() => onOpen(f.path, f.name)}
    >
      {selectMode && (
        <div
          className={`absolute top-1 left-1 z-20 h-5 w-5 rounded border-2 flex items-center justify-center cursor-pointer transition-colors ${
            isSelected ? "bg-primary border-primary" : "border-primary/50 bg-background/80"
          }`}
          onClick={(e) => { e.stopPropagation(); onToggleSelect(f.path) }}
        >
          {isSelected && <Check className="h-3 w-3 text-primary-foreground" />}
        </div>
      )}
      {label && label !== "none" && (
        <div className={`absolute top-1 right-1 h-2 w-2 rounded-full ${LABEL_CLASS_MAP[label] || "bg-muted"} z-10`} />
      )}

      <div className="aspect-square bg-muted relative overflow-hidden">
        {!selectMode && flag && (
          <div className={`absolute top-1 left-1 w-5 h-5 rounded-full flex items-center justify-center text-xs z-20 ${
            flag === "pick" ? "bg-green-500 text-white" : "bg-red-500 text-white"
          }`}>
            {flag === "pick" ? "✓" : "✕"}
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-br from-muted to-muted/50" />
        {isImageFile(f.suffix) ? (
          <div className="relative group w-full h-full absolute inset-0">
            <img
              src={convertFileSrc(f.path)}
              alt={f.name}
              className="w-full h-full object-cover"
              loading="lazy"
              decoding="async"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none"
                if ((e.target as HTMLImageElement).parentElement) {
                  (e.target as HTMLImageElement).parentElement!.classList.add("fallback-icon")
                }
              }}
            />
            {exifData?.exif && (exifData.exif.iso || exifData.exif.aperture || exifData.exif.shutter || exifData.exif.focal_length) && (
              <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-[10px] p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                ISO {exifData.exif.iso} · f/{exifData.exif.aperture} · {exifData.exif.shutter}s · {exifData.exif.focal_length}mm
              </div>
            )}
          </div>
        ) : isVideoFile(f.suffix) ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <Film className="w-8 h-8 text-muted-foreground/40" />
          </div>
        ) : isAudioFile(f.suffix) ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <Music className="w-8 h-8 text-muted-foreground/40" />
          </div>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <File className="w-8 h-8 text-muted-foreground/40" />
          </div>
        )}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center opacity-0 group-hover:opacity-100">
          <Button
            size="sm"
            variant="secondary"
            className="h-7 text-xs"
            onClick={(e) => { e.stopPropagation(); onOpen(f.path, f.name) }}
          >
            {t("Open", "Öffnen")}
          </Button>
        </div>
      </div>

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
              <DropdownMenuItem onClick={() => onOpen(f.path, f.name)} disabled={isActionLoading}>
                <ExternalLink className="h-3.5 w-3.5 mr-2" />
                {t("Open", "Öffnen")}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onReveal(f.path)}>
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
                    <DropdownMenuItem key={c.key} onClick={() => onSetLabel(f.path, c.key)}>
                      <div className={`h-3 w-3 rounded-full ${c.bg} mr-2`} />
                      {t(c.label, c.label)}
                      {label === c.key && <Check className="h-3 w-3 ml-auto" />}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuSubContent>
              </DropdownMenuSub>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => onRenameDialog({ path: f.path, name: f.name })}>
                <Pencil className="h-3.5 w-3.5 mr-2" />
                {t("Rename", "Umbenennen")}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onDeleteDialog({ path: f.path, name: f.name })}
                className="text-red-500"
              >
                <Trash2 className="h-3.5 w-3.5 mr-2" />
                {t("Delete", "Löschen")}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <div className="px-2 py-1">
                <PickRejectBar
                  flagState={flag || "none"}
                  onFlag={(state) => onFlag(f.path, state)}
                  compact
                />
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div className="flex items-center justify-between mt-1">
          <Badge className={`text-xs px-1 py-0 ${SUFFIX_COLORS[f.suffix] || "bg-muted text-muted-foreground"}`}>
            {f.suffix}
          </Badge>
          <span className="text-xs text-muted-foreground">{formatSize(f.size)}</span>
        </div>
        <div className="mt-0.5">
          <StarRating
            value={rating}
            onChange={(v) => onRatingChange(f.path, v)}
            size="sm"
          />
        </div>
        <div className="mt-1">
          <TagInput
            tags={tags}
            onChange={(newTags) => onUpdateTags(f.path, newTags)}
          />
        </div>
      </CardContent>
    </Card>
  )
})

export default function LibraryPage() {
  const t = useT()
  const [rootDir, setRootDir] = useState(() => localStorage.getItem("library_root") || localStorage.getItem("default_source_dir") || "")
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<LibraryBrowsePaginatedResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showHint, dismissHint] = useFirstRunHint("library")
  const [filter, setFilter] = useState("")
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(48)
  const [loadedPages, setLoadedPages] = useState<Map<number, LibraryBrowsePaginatedResult["files"]>>(new Map())
  const loadedPagesRef = useRef<Map<number, LibraryBrowsePaginatedResult["files"]>>(new Map())
  const [loadingPages, setLoadingPages] = useState<Set<number>>(new Set())
  const [deleteDialog, setDeleteDialog] = useState<{ path: string; name: string } | null>(null)
  const [renameDialog, setRenameDialog] = useState<{ path: string; name: string } | null>(null)
  const [renameValue, setRenameValue] = useState("")
  const [quickRename, setQuickRename] = useState<{ path: string; name: string } | null>(null)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
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

  const [selectedFile, setSelectedFile] = useState<LibraryBrowsePaginatedResult["files"][0] | null>(null)

  const [allTags, setAllTags] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem("library_tags") || "[]") }
    catch { return [] }
  })
  const [fileTags, setFileTags] = useState<Record<string, string[]>>(() => {
    try { return JSON.parse(localStorage.getItem("library_file_tags") || "{}") }
    catch { return {} }
  })
  const [batchTagInput, setBatchTagInput] = useState("")
  const [tagFilter, setTagFilter] = useState<string[]>([])

  const [fileFlags, setFileFlags] = useState<Record<string, "pick" | "reject">>(() => {
    try { return JSON.parse(localStorage.getItem("library_flags") || "{}") }
    catch { return {} }
  })
  const [flagFilter, setFlagFilter] = useState<"all" | "pick" | "reject" | "unflagged">("all")
  const [splitViewOpen, setSplitViewOpen] = useState(false)
  const [showEmailShare, setShowEmailShare] = useState(false)
  const [showNetworkHint, setShowNetworkHint] = useState(false)

  const [elapsed, setElapsed] = useState(0)
  const elapsedRef = useRef<NodeJS.Timeout | null>(null)

  const navigate = useNavigate()

  const [enrichedData, setEnrichedData] = useState<EnrichedFile | null>(null)

  const [magicResult, setMagicResult] = useState<MagicDetectResult | null>(null)

  const [healthResult, setHealthResult] = useState<FileHealthResult | null>(null)

  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  const [exifFilters, setExifFilters] = useState<{
    camera?: string
    lens?: string
    isoMin?: number
    isoMax?: number
    apertureMin?: string
  }>({})
  const [fileTypes, setFileTypes] = useState<string[]>([])
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [sizeMin, setSizeMin] = useState("")
  const [sizeMax, setSizeMax] = useState("")
  const [sortBy, setSortBy] = useState<"name" | "date" | "size" | "">("")
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc")
  const [filterDropdownOpen, setFilterDropdownOpen] = useState(false)
  const [isNarrow, setIsNarrow] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const [compareDir, setCompareDir] = useState("")
  const [compareData, setCompareData] = useState<LibraryBrowsePaginatedResult | null>(null)
  const [comparing, setComparing] = useState(false)
  const [peopleSearch, setPeopleSearch] = useState("")
  const [peopleResults, setPeopleResults] = useState<string[]>([])

  const scrollRef = useRef(0)

  const runCompare = async () => {
    if (!compareDir) return
    setComparing(true)
    try {
      const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
      const result = await libraryBrowsePaginated({ root_dir: compareDir, page: 0, page_size: 0 })
      setCompareData(result)
    } catch (e) { console.error(e) }
    finally { setComparing(false) }
  }

  useEffect(() => {
    if (!selectedFile) { setEnrichedData(null); return }
    let cancelled = false
    dedupedCall(`enrich:${selectedFile.path}`, () =>
      cachedCall(`enrich:${selectedFile.path}`, () => enrichFile(selectedFile.path))
    ).then(data => {
      if (!cancelled) setEnrichedData(data)
    }).catch(() => {
      if (!cancelled) setEnrichedData(null)
    })
    return () => { cancelled = true }
  }, [selectedFile])

  useEffect(() => {
    if (!selectedFile) { setMagicResult(null); return }
    let cancelled = false
    magicDetect(selectedFile.path).then(data => {
      if (!cancelled) setMagicResult(data)
    }).catch(() => {
      if (!cancelled) setMagicResult(null)
    })
    return () => { cancelled = true }
  }, [selectedFile])

  useEffect(() => {
    if (!selectedFile) { setHealthResult(null); return }
    let cancelled = false
    healthCheckFile(selectedFile.path).then(data => {
      if (!cancelled) setHealthResult(data)
    }).catch(() => {
      if (!cancelled) setHealthResult(null)
    })
    return () => { cancelled = true }
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
    if (loadedPagesRef.current.has(pageNum)) return

    setLoadingPages(prev => new Set(prev).add(pageNum))
    try {
      const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
      const r = await libraryBrowsePaginated({
        root_dir: rootDir,
        page: pageNum,
        page_size: pageSize,
      })
      setLoadedPages(prev => {
        const next = new Map(prev)
        next.set(pageNum, r.files)
        if (next.size > 5) {
          const keys = [...next.keys()].sort((a, b) => Math.abs(a - pageNum) - Math.abs(b - pageNum))
          for (const k of keys.slice(5)) next.delete(k)
        }
        loadedPagesRef.current = next
        return next
      })
      if (pageNum === 0) {
        setData(r)
      }
    } catch (e) {
      console.error(`Failed to load page ${pageNum}:`, e)
    } finally {
      setLoadingPages(prev => {
        const next = new Set(prev)
        next.delete(pageNum)
        return next
      })
    }
  }, [rootDir, pageSize])

  const browse = useCallback(async () => {
    if (!rootDir) return
    setLoading(true); setError(null); setPage(0); setLoadedPages(new Map())
    loadedPagesRef.current = new Map()
    localStorage.setItem("library_root", rootDir)
    setElapsed(0)
    elapsedRef.current = setInterval(() => setElapsed(e => e + 1), 1000)
    try {
      await loadPageData(0)
    } catch (e) { setError(String(e)) }
    finally {
      setLoading(false)
      if (elapsedRef.current) { clearInterval(elapsedRef.current); elapsedRef.current = null }
    }
  }, [rootDir, loadPageData])

  useEffect(() => {
    if (!data || loading) return
    loadPageData(page)
    const timers: ReturnType<typeof setTimeout>[] = []
    if (page + 1 < (data.total_pages || 1)) {
      timers.push(setTimeout(() => loadPageData(page + 1), 200))
    }
    if (page - 1 >= 0) {
      timers.push(setTimeout(() => loadPageData(page - 1), 400))
    }
    return () => { timers.forEach(clearTimeout) }
  }, [page])

  useEffect(() => {
    setSelectedPaths(new Set())
  }, [page])

  useEffect(() => {
    window.scrollTo(0, scrollRef.current)
  }, [page])

  useEffect(() => {
    const check = () => setIsNarrow(window.innerWidth < 768)
    check()
    window.addEventListener("resize", check)
    return () => window.removeEventListener("resize", check)
  }, [])

  useEffect(() => {
    const handleScroll = () => { scrollRef.current = window.scrollY }
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return

      if (e.key === "Escape") {
        setSelectedFile(null)
        setQuickRename(null)
        return
      }

      if (!selectedFile) return

      switch (e.key) {
        case "p": setFlag(selectedFile.path, "pick"); break
        case "x": setFlag(selectedFile.path, "reject"); break
        case "u": setFlag(selectedFile.path, "none"); break
        case "Delete": setDeleteDialog({ path: selectedFile.path, name: selectedFile.name }); break
        case "F2": setQuickRename({ path: selectedFile.path, name: selectedFile.name }); break
      }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [selectedFile, setFlag])

  const handleOpen = useCallback(async (path: string, name: string) => {
    setActionLoading(path)
    try {
      await fileOpen(path)
      trackRecentlyViewed(path, name)
    }
    catch (e) { setError(String(e)) }
    finally { setActionLoading(null) }
  }, [])

  const handleReveal = useCallback(async (path: string) => {
    try { await fileReveal(path) }
    catch (e) { setError(String(e)) }
  }, [])

  const handleDeleteConfirm = async () => {
    if (!deleteDialog) return
    try {
      await fileDelete(deleteDialog.path)
      setDeleteDialog(null)
      const next = new Map(loadedPages)
      next.delete(page)
      setLoadedPages(next)
      loadedPagesRef.current = next
      loadPageData(page)
    } catch (e) { setError(String(e)) }
  }

  const handleSetLabel = useCallback((filePath: string, color: string) => {
    setLabels(prev => {
      const next = { ...prev, [filePath]: color }
      localStorage.setItem("library_labels", JSON.stringify(next))
      return next
    })
  }, [])

  const updateFileTags = useCallback((path: string, tags: string[]) => {
    setFileTags(prev => {
      const next = { ...prev, [path]: tags }
      localStorage.setItem("library_file_tags", JSON.stringify(next))
      return next
    })
    setAllTags(prevAll => {
      const tagSet = new Set(prevAll)
      tags.forEach(t => tagSet.add(t))
      Object.values(fileTags).forEach(ts => ts.forEach(t => tagSet.add(t)))
      const newAll = Array.from(tagSet).sort()
      localStorage.setItem("library_tags", JSON.stringify(newAll))
      return newAll
    })
  }, [fileTags])

  const handleRenameConfirm = async () => {
    if (!renameDialog || !renameValue.trim()) return
    try {
      await fileRename(renameDialog.path, renameValue.trim())
      setRenameDialog(null)
      const next = new Map(loadedPages)
      next.delete(page)
      setLoadedPages(next)
      loadedPagesRef.current = next
      loadPageData(page)
    } catch (e) { setError(String(e)) }
  }

  const toggleSelect = useCallback((path: string) => {
    setSelectedPaths(prev => {
      const next = new Set(prev)
      if (next.has(path)) next.delete(path)
      else next.add(path)
      return next
    })
  }, [])

  const selectAll = () => {
    if (selectedPaths.size === sortedFiles.length) {
      setSelectedPaths(new Set())
    } else {
      setSelectedPaths(new Set(sortedFiles.map(f => f.path)))
    }
  }

  const currentFiles = loadedPages.get(page) || []
  const totalPages = data?.total_pages || 1

  useEffect(() => {
    if (!peopleSearch.trim() || !currentFiles.length) {
      setPeopleResults([])
      return
    }
    const search = peopleSearch.toLowerCase()
    const matches = currentFiles
      .filter(f => f.relative?.toLowerCase().includes(search) || f.name?.toLowerCase().includes(search))
      .map(f => f.path)
    setPeopleResults(matches)
  }, [peopleSearch, currentFiles])

  const crossDupes = useMemo(() => {
    if (!compareData || !data) return new Set<string>()
    const compareNames = new Set(compareData.files.map((f) => f.name))
    const compareSizes = new Map(compareData.files.map((f) => [f.name, f.size]))
    return new Set(
      currentFiles
        .filter((f) => compareNames.has(f.name) && compareSizes.get(f.name) === f.size)
        .map((f) => f.path)
    )
  }, [compareData, data, currentFiles])

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
    if (fileTypes.length > 0) {
      files = files.filter(f => fileTypes.includes(f.category))
    }
    if (dateFrom) {
      files = files.filter(f => f.modified >= dateFrom)
    }
    if (dateTo) {
      files = files.filter(f => f.modified <= dateTo + "T23:59:59")
    }
    if (sizeMin) {
      const min = Number(sizeMin) * 1024
      files = files.filter(f => f.size >= min)
    }
    if (sizeMax) {
      const max = Number(sizeMax) * 1024
      files = files.filter(f => f.size <= max)
    }
    if (sortBy) {
      files = [...files].sort((a, b) => {
        let cmp = 0
        if (sortBy === "name") cmp = a.name.localeCompare(b.name)
        else if (sortBy === "date") cmp = a.modified.localeCompare(b.modified)
        else if (sortBy === "size") cmp = a.size - b.size
        return sortDir === "desc" ? -cmp : cmp
      })
    }
    return files
  }, [currentFiles, filter, tagFilter, fileTags, flagFilter, fileFlags, fileTypes, dateFrom, dateTo, sizeMin, sizeMax, sortBy, sortDir])

  const activeFilterCount = useMemo(
    () => [fileTypes.length > 0, !!dateFrom, !!dateTo, flagFilter !== "all", tagFilter.length > 0].filter(Boolean).length,
    [fileTypes.length, dateFrom, dateTo, flagFilter, tagFilter.length]
  )

  const slideshowFiles = useMemo(
    () => currentFiles.map(f => ({ path: f.path, name: f.name })),
    [currentFiles]
  )

  const splitViewFiles = useMemo(
    () => currentFiles.filter(f => selectedPaths.has(f.path)).map(f => ({ path: f.path, name: f.name })),
    [currentFiles, selectedPaths]
  )

  const handleDeleteDialog = useCallback((item: { path: string; name: string }) => setDeleteDialog(item), [])
  const handleRenameDialog = useCallback((item: { path: string; name: string }) => {
    setRenameDialog(item)
    setRenameValue(item.name)
  }, [])

  const handleSetRating = useCallback((path: string, value: number) => {
    setRatings(prev => {
      const next = { ...prev, [path]: value }
      localStorage.setItem("library_ratings", JSON.stringify(next))
      return next
    })
  }, [])

  const metadataScore = useMemo(() => {
    if (!enrichedData) return { score: 0, grade: "D" }
    let present = 0
    let total = 0
    const exif = enrichedData.exif
    if (exif) {
      total += 8
      if (exif.camera) present++
      if (exif.lens) present++
      if (exif.iso != null) present++
      if (exif.aperture) present++
      if (exif.shutter) present++
      if (exif.focal_length) present++
      if (exif.date_taken) present++
      if (exif.megapixels != null) present++
    }
    if (enrichedData.gps) { total++; present++ }
    if (enrichedData.faces && enrichedData.faces.length > 0) { total++; present++ }
    if (enrichedData.colors && enrichedData.colors.length > 0) { total++; present++ }
    if (enrichedData.auto_tags && enrichedData.auto_tags.length > 0) { total++; present++ }
    const score = total > 0 ? Math.round((present / total) * 100) : 0
    const grade = score >= 90 ? "A" : score >= 75 ? "B" : score >= 50 ? "C" : "D"
    return { score, grade }
  }, [enrichedData])

  const healthScore = useMemo(() => {
    if (!healthResult) return { score: 100, issues: 0 }
    const issues = healthResult.issues.length + healthResult.warnings.length
    const score = healthResult.healthy ? (issues === 0 ? 100 : 80) : Math.max(0, 60 - issues * 10)
    return { score, issues }
  }, [healthResult])

  return (
    <>
      <PageHeader
        title={t("Library", "Bibliothek")}
        subtitle={t("Browse your media files with actions.", "Medien durchsuchen mit Aktionen.")}
      />
      {showHint && (
        <div data-hint className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800/30 rounded-lg p-3 mb-4 mx-6 text-sm">
          <p>{t("Browse, filter, rate, and manage your organized media files. Search, sort, and tag to keep your library tidy.", "Durchstöbere, filtere, bewerte und verwalte deine organisierten Mediendateien. Suche, sortiere und tagge, um deine Bibliothek sauber zu halten.")}</p>
          <button onClick={dismissHint}
            className="text-xs text-blue-500 dark:text-blue-400 mt-1 hover:underline">{t("Got it", "Verstanden")}</button>
        </div>
      )}
      <main
        className="flex flex-1 gap-4 p-6"
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
        <div className="flex-1 max-w-5xl space-y-4">



      {/* Search bar */}
      <div className="flex gap-2 relative">
        <Input
          value={rootDir}
          onChange={e => setRootDir(e.target.value)}
          placeholder={t("Root directory (e.g. organized folder)", "Stammverzeichnis (z.B. organisierter Ordner)")}
          className="text-xs flex-1"
          onKeyDown={e => e.key === "Enter" && browse()}
        />
        <Button variant="ghost" size="sm" className="text-xs h-6" onClick={() => setShowNetworkHint(p => !p)}>
          <HardDrive className="h-3 w-3 mr-1" />
          {t("Network", "Netzwerk")}
        </Button>
        {showNetworkHint && (
          <div className="absolute top-full left-0 mt-1 bg-background border rounded p-2 shadow-lg z-10 w-64">
            <p className="text-xs font-medium mb-1">{t("Common network paths:", "Häufige Netzwerkpfade:")}</p>
            {[
              "\\\\NAS\\Photos",
              "\\\\SERVER\\Media",
              "Z:\\Photos",
              "/mnt/nas/photos",
              "/Volumes/Media",
            ].map(p => (
              <button key={p} className="block text-xs text-left py-0.5 hover:bg-muted rounded px-1 w-full"
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

      {error && <p role="alert" className="text-sm text-red-400">{error}</p>}

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
                <span className="text-xs text-muted-foreground">{t("Filter by tag:", "Nach Tag filtern:")}</span>
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
            <div className="flex items-center gap-1 flex-wrap">
              {isNarrow ? (
                <DropdownMenu open={filterDropdownOpen} onOpenChange={setFilterDropdownOpen}>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm" className="text-xs h-7 gap-1">
                      <SlidersHorizontal className="h-3 w-3" />
                      {t("Quick filters", "Schnellfilter")}
                      {activeFilterCount > 0 && <Badge className="ml-1 h-4 px-1 text-xs">{activeFilterCount}</Badge>}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-48">
                    <DropdownMenuItem onClick={() => {
                      setFileTypes([]); setDateFrom(""); setDateTo(""); setFlagFilter("all")
                      setSizeMin(""); setSizeMax(""); setSortBy(""); setPage(0)
                    }}>
                      {t("All", "Alle")}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => { setFileTypes(["photo"]); setPage(0) }}>
                      {t("Photos", "Fotos")}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => { setFileTypes(["video"]); setPage(0) }}>
                      {t("Videos", "Videos")}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => { setFileTypes(["raw"]); setPage(0) }}>
                      {t("RAW", "RAW")}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => { setFlagFilter(flagFilter === "pick" ? "all" : "pick"); setPage(0) }}>
                      {t("Picks", "Auswahl")}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => { setFlagFilter(flagFilter === "reject" ? "all" : "reject"); setPage(0) }}>
                      {t("Rejects", "Abgelehnt")}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => { setSortBy("date"); setSortDir("desc"); setPage(0) }}>
                      {t("Newest first", "Neueste zuerst")}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => { setSortBy("size"); setSortDir("desc"); setPage(0) }}>
                      {t("Largest first", "Größte zuerst")}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <>
              <button onClick={() => {
                  setFileTypes([]); setDateFrom(""); setDateTo(""); setFlagFilter("all")
                  setSizeMin(""); setSizeMax(""); setSortBy(""); setPage(0)
                }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  (!fileTypes.length && !dateFrom && !dateTo && flagFilter === "all" && !sortBy)
                    ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                {t("All", "Alle")}
              </button>
              <button onClick={() => { setFileTypes(["photo"]); setPage(0) }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  fileTypes.length === 1 && fileTypes[0] === "photo" ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                🖼️ {t("Photos", "Fotos")}
              </button>
              <button onClick={() => { setFileTypes(["video"]); setPage(0) }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  fileTypes.length === 1 && fileTypes[0] === "video" ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                🎬 {t("Videos", "Videos")}
              </button>
              <button onClick={() => { setFileTypes(["raw"]); setPage(0) }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  fileTypes.length === 1 && fileTypes[0] === "raw" ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                📷 RAW
              </button>
              <button onClick={() => {
                  const today = new Date().toISOString().slice(0, 10)
                  setDateFrom(today); setDateTo(today); setPage(0)
                }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  dateFrom && dateFrom === dateTo ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                📅 {t("Today", "Heute")}
              </button>
              <button onClick={() => {
                  const now = new Date()
                  const weekAgo = new Date(now.getTime() - 7 * 86400000).toISOString().slice(0, 10)
                  setDateFrom(weekAgo); setDateTo(now.toISOString().slice(0, 10)); setPage(0)
                }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  dateFrom && dateTo && !(dateFrom === dateTo) ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                📅 {t("Week", "Woche")}
              </button>
              <button onClick={() => {
                  const now = new Date()
                  const monthAgo = new Date(now.getTime() - 30 * 86400000).toISOString().slice(0, 10)
                  setDateFrom(monthAgo); setDateTo(now.toISOString().slice(0, 10)); setPage(0)
                }}
                className="text-xs px-2 py-0.5 rounded-full border text-muted-foreground hover:text-foreground transition-colors">
                📅 {t("Month", "Monat")}
              </button>
              <button onClick={() => { setFlagFilter(flagFilter === "pick" ? "all" : "pick"); setPage(0) }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  flagFilter === "pick" ? "bg-green-500 text-white border-green-500" : "text-muted-foreground hover:text-foreground"
                }`}>
                ✅ {t("Picks", "Picks")}
              </button>
              <button onClick={() => { setFlagFilter(flagFilter === "reject" ? "all" : "reject"); setPage(0) }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  flagFilter === "reject" ? "bg-red-500 text-white border-red-500" : "text-muted-foreground hover:text-foreground"
                }`}>
                ❌ {t("Rejects", "Rejects")}
              </button>
              <button onClick={() => { setSortBy("date"); setSortDir(sortBy === "date" && sortDir === "desc" ? "asc" : "desc"); setPage(0) }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  sortBy === "date" ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                🆕 {sortBy === "date" && sortDir === "desc" ? t("Newest", "Neueste") : sortBy === "date" ? t("Oldest", "Älteste") : t("By date", "Nach Datum")}
              </button>
              <button onClick={() => { setSortBy("size"); setSortDir(sortBy === "size" && sortDir === "desc" ? "asc" : "desc"); setPage(0) }}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  sortBy === "size" ? "bg-primary text-primary-foreground border-primary" : "text-muted-foreground hover:text-foreground"
                }`}>
                📦 {sortBy === "size" && sortDir === "desc" ? t("Largest", "Größte") : sortBy === "size" ? t("Smallest", "Kleinste") : t("By size", "Nach Größe")}
              </button>
                </>
              )}
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
              className="text-xs">
              <SlidersHorizontal className="h-3 w-3 mr-1" />
              {showAdvancedFilters ? t("Hide filters", "Filter verbergen") : t("Advanced filters", "Erweiterte Filter")}
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Input value={compareDir} onChange={e => setCompareDir(e.target.value)}
              placeholder={t("Compare with directory...", "Mit Verzeichnis vergleichen...")}
              className="text-xs h-7 w-40" />
            <Button size="sm" variant="outline" onClick={runCompare} disabled={comparing || !compareDir}
              className="h-7 text-xs">
              <ArrowLeftRight className="h-3 w-3 mr-1" />
              {comparing ? <Loader2 className="h-3 w-3 animate-spin" /> : t("Compare", "Vergleichen")}
            </Button>
            {compareData && (
              <Badge className="text-xs">
                {crossDupes.size} {t("matches", "Treffer")}
              </Badge>
            )}
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
            <select
              value={pageSize}
              onChange={e => {
                const newSize = Number(e.target.value)
                setPageSize(newSize)
                setPage(0)
                setLoadedPages(new Map())
                loadedPagesRef.current = new Map()
                loadPageData(0)
              }}
              className="text-xs border rounded px-2 py-1 bg-background"
              aria-label={t("Items per page", "Einträge pro Seite")}
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
          <div className="flex items-center gap-2 w-full">
            <input placeholder={t("Person name in path...", "Personenname im Pfad...")}
              className="text-xs border rounded px-2 py-1 w-48 bg-background"
              value={peopleSearch}
              onChange={e => setPeopleSearch(e.target.value)}
              aria-label={t("Person name filter", "Personennamen-Filter")} />
            {peopleResults.length > 0 && (
              <Badge variant="secondary" className="text-xs">{peopleResults.length} {t("matches", "Treffer")}</Badge>
            )}
          </div>
          <input placeholder={t("Camera model...", "Kamera-Modell...")}
            className="text-xs border rounded px-2 py-1 w-32 bg-background"
            value={exifFilters.camera || ""}
            onChange={e => setExifFilters(prev => ({...prev, camera: e.target.value || undefined}))}
            aria-label={t("Camera model filter", "Kamera-Modell-Filter")} />
          <input placeholder={t("Lens...", "Objektiv...")}
            className="text-xs border rounded px-2 py-1 w-32 bg-background"
            value={exifFilters.lens || ""}
            onChange={e => setExifFilters(prev => ({...prev, lens: e.target.value || undefined}))}
            aria-label={t("Lens filter", "Objektiv-Filter")} />
          <input placeholder={t("ISO min", "ISO min")} type="number"
            className="text-xs border rounded px-2 py-1 w-20 bg-background"
            onChange={e => setExifFilters(prev => ({...prev, isoMin: e.target.value ? Number(e.target.value) : undefined}))}
            aria-label={t("ISO minimum", "ISO-Minimum")} />
          <input placeholder={t("ISO max", "ISO max")} type="number"
            className="text-xs border rounded px-2 py-1 w-20 bg-background"
            onChange={e => setExifFilters(prev => ({...prev, isoMax: e.target.value ? Number(e.target.value) : undefined}))}
            aria-label={t("ISO maximum", "ISO-Maximum")} />
          <input placeholder={t("Size min (KB)", "Größe min (KB)")} type="number"
            className="text-xs border rounded px-2 py-1 w-24 bg-background"
            value={sizeMin}
            onChange={e => setSizeMin(e.target.value)}
            aria-label={t("File size minimum", "Dateigröße-Minimum")} />
          <input placeholder={t("Size max (KB)", "Größe max (KB)")} type="number"
            className="text-xs border rounded px-2 py-1 w-24 bg-background"
            value={sizeMax}
            onChange={e => setSizeMax(e.target.value)}
            aria-label={t("File size maximum", "Dateigröße-Maximum")} />
          {(exifFilters.camera || exifFilters.lens || exifFilters.isoMin || exifFilters.isoMax) && (
            <Button variant="ghost" size="sm" className="text-xs"
              onClick={() => setExifFilters({})}>
              {t("Clear", "Löschen")}
            </Button>
          )}
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm flex items-center justify-center">
          <div className="bg-card border rounded-xl shadow-xl p-8 max-w-md w-full mx-4 text-center space-y-4">
            <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
            <h2 className="text-lg font-semibold">{t("Scanning Library", "Bibliothek wird gescannt")}</h2>
            <p className="text-sm text-muted-foreground">
              {rootDir && (
                <span className="break-all">{rootDir.split("/").pop() || rootDir.split("\\").pop()}</span>
              )}
            </p>
            
            <div className="space-y-2">
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary rounded-full transition-all duration-500 animate-pulse"
                  style={{ width: `${Math.min(95, (elapsed / 30) * 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{t("Scanning files...", "Dateien werden gescannt...")}</span>
                <span>{elapsed}s</span>
              </div>
            </div>

            <p className="text-xs text-muted-foreground">
              {t("This may take a moment for large libraries.", "Bei großen Bibliotheken kann dies einen Moment dauern.")}
            </p>
          </div>
        </div>
      )}

      {/* Loading page skeleton */}
      {!loading && data && loadingPages.has(page) && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-2">
          {Array.from({ length: Math.min(pageSize, 12) }).map((_, i) => (
            <Card key={i} className="overflow-hidden">
              <Skeleton className="aspect-square w-full" />
              <CardContent className="p-2"><Skeleton className="h-3 w-3/4" /></CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* File grid */}
      {!loading && data && currentFiles.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-2">
          {sortedFiles.map((f) => (
            <FileCard
              key={f.path}
              f={f}
              isSelected={selectedPaths.has(f.path)}
              isCrossDupe={crossDupes.has(f.path)}
              label={labels[f.path]}
              flag={fileFlags[f.path]}
              rating={ratings[f.path] || 0}
              tags={fileTags[f.path] || []}
              isActionLoading={actionLoading === f.path}
              selectMode={selectMode}
              exifData={selectedFile?.path === f.path ? enrichedData : null}
              onOpen={handleOpen}
              onReveal={handleReveal}
              onSetLabel={handleSetLabel}
              onFlag={setFlag}
              onDeleteDialog={handleDeleteDialog}
              onRenameDialog={handleRenameDialog}
              onToggleSelect={toggleSelect}
              onSelectFile={setSelectedFile}
              onUpdateTags={updateFileTags}
              onRatingChange={handleSetRating}
            />
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
          <div className="flex items-center gap-4">
            <MetadataScoreBadge score={metadataScore.score} grade={metadataScore.grade} />
            <HealthIndicator score={healthScore.score} issues={healthScore.issues} />
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <span className="text-muted-foreground">{t("Name", "Name")}</span>
            <span className="truncate">{selectedFile.name}</span>
            <span className="text-muted-foreground">{t("Type", "Typ")}</span>
            <span className="flex items-center gap-1 truncate">
              {selectedFile.category || selectedFile.suffix}
              {magicResult?.mismatch && (
                <ExtensionMismatchWarning
                  extension={magicResult.extension || selectedFile.suffix}
                  detectedType={magicResult.mime_type || magicResult.description || "unknown"}
                />
              )}
            </span>
            <span className="text-muted-foreground">{t("Size", "Größe")}</span>
            <span>{formatSize(selectedFile.size)}</span>
            <span className="text-muted-foreground">{t("Path", "Pfad")}</span>
            <span className="truncate text-xs" title={selectedFile.path}>{selectedFile.relative}</span>
          </div>
          {selectedFile && selectedFile.suffix && ['.cr2', '.cr3', '.nef', '.arw', '.dng'].includes(selectedFile.suffix) && (
            <Badge variant="secondary" className="text-xs">RAW</Badge>
          )}
          {selectedFile && isVideoFile(selectedFile.suffix) && (
            <div className="mt-3">
              <video
                src={convertFileSrc(selectedFile.path)}
                controls
                className="w-full max-h-64 rounded"
                preload="metadata"
              />
            </div>
          )}
          {selectedFile && isAudioFile(selectedFile.suffix) && (
            <audio src={convertFileSrc(selectedFile.path)} controls className="w-full mt-2" />
          )}
          {enrichedData?.exif?.megapixels != null && (enrichedData.exif.megapixels as number) > 6 && (
            <p className="text-xs text-amber-500 mt-1">
              {t("High resolution image \u2014 may take longer to load", "Hochaufl\u00f6sendes Bild \u2014 Laden kann l\u00e4nger dauern")}
            </p>
          )}
          {enrichedData?.exif && Object.keys(enrichedData.exif).length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-xs font-semibold">{t("EXIF", "EXIF")}</span>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs mt-1">
                {enrichedData.exif.camera && <><span className="text-muted-foreground">{t("Camera", "Kamera")}</span><span className="truncate">{String(enrichedData.exif.camera)}</span></>}
                {enrichedData.exif.lens && <><span className="text-muted-foreground">{t("Lens", "Objektiv")}</span><span className="truncate">{String(enrichedData.exif.lens)}</span></>}
                {enrichedData.exif.iso != null && <><span className="text-muted-foreground">ISO</span><span>{String(enrichedData.exif.iso)}</span></>}
                {enrichedData.exif.aperture && <><span className="text-muted-foreground">{t("Aperture", "Blende")}</span><span>f/{String(enrichedData.exif.aperture)}</span></>}
                {enrichedData.exif.shutter && <><span className="text-muted-foreground">{t("Shutter", "Verschluss")}</span><span>{String(enrichedData.exif.shutter)}s</span></>}
                {enrichedData.exif.focal_length && <><span className="text-muted-foreground">{t("Focal", "Brennweite")}</span><span>{String(enrichedData.exif.focal_length)}mm</span></>}
                {enrichedData.exif.date_taken && <><span className="text-muted-foreground">{t("Date", "Datum")}</span><span className="truncate">{String(enrichedData.exif.date_taken)}</span></>}
                {enrichedData.exif.megapixels != null && <><span className="text-muted-foreground">MP</span><span>{String(enrichedData.exif.megapixels)}</span></>}
              </div>
            </div>
          )}
          {enrichedData?.auto_tags && enrichedData.auto_tags.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-xs font-semibold">{t("Auto Tags", "Auto-Tags")}</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {enrichedData.auto_tags.map(tag => (
                  <Badge key={tag} variant="secondary" className="text-[9px]">{tag.replace(':', ': ')}</Badge>
                ))}
              </div>
            </div>
          )}
          {enrichedData?.faces && enrichedData.faces.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-xs font-semibold">{t("People", "Personen")}</span>
              <div className="mt-1 space-y-1">
                {enrichedData.faces.map((face, i) => (
                  <Badge key={i} variant="secondary" className="text-xs">{face.name}</Badge>
                ))}
              </div>
            </div>
          )}
          {enrichedData?.colors && enrichedData.colors.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-xs font-semibold">{t("Colors", "Farben")}</span>
              <div className="mt-1 flex gap-1">
                {enrichedData.colors.map((c, i) => (
                  <span key={i} className="inline-block h-4 w-4 rounded-full border" style={{ backgroundColor: c }} title={c} />
                ))}
              </div>
            </div>
          )}
          {enrichedData?.has_duplicates && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-xs text-yellow-500 font-semibold">{t("Has duplicates", "Hat Duplikate")}</span>
            </div>
          )}
          <div className="flex items-center justify-between mt-3 pt-3 border-t">
            <span className="text-xs text-muted-foreground">{t("Flag", "Markierung")}</span>
            <PickRejectBar
              flagState={fileFlags[selectedFile.path] || "none"}
              onFlag={(state) => setFlag(selectedFile.path, state)}
              compact
            />
          </div>
          <div className="mt-3 pt-3 border-t">
            <span className="text-xs text-muted-foreground">{t("Tags", "Tags")}</span>
            <div className="mt-1">
              <TagInput
                tags={fileTags[selectedFile.path] || []}
                onChange={(tags) => updateFileTags(selectedFile.path, tags)}
              />
            </div>
          </div>
          {enrichedData?.auto_tags && enrichedData.auto_tags.length > 0 && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-xs text-muted-foreground">{t("Auto tags", "Auto-Tags")}</span>
              <div className="mt-1">
                <TagCloud
                  tags={enrichedData.auto_tags}
                  onTagClick={(tag) => {
                    setTagFilter(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag])
                  }}
                  max={15}
                />
              </div>
            </div>
          )}
          {enrichedData?.gps?.lat != null && enrichedData.gps.lon != null && (
            <div className="mt-3 pt-3 border-t">
              <span className="text-xs text-muted-foreground">{t("GPS", "GPS")}</span>
              <div className="mt-1 text-xs text-muted-foreground">
                {String(enrichedData.gps.lat)}, {String(enrichedData.gps.lon)}
              </div>
              <div className="mt-2 rounded overflow-hidden border">
                <img
                  src={`https://staticmap.openstreetmap.de/staticmap.php?center=${encodeURIComponent(String(enrichedData.gps.lat))},${encodeURIComponent(String(enrichedData.gps.lon))}&zoom=12&size=400x200&markers=${encodeURIComponent(String(enrichedData.gps.lat))},${encodeURIComponent(String(enrichedData.gps.lon))},red-pushpin`}
                  alt={t("Map location", "Kartenposition")}
                  className="w-full h-32 object-cover"
                  width="400" height="200" loading="lazy" decoding="async"
                />
              </div>
              <div className="mt-2">
                <Button variant="outline" size="sm" onClick={() => {
                  const lat = String(enrichedData.gps!.lat).replace(/deg|'|"/g, "").trim()
                  const lon = String(enrichedData.gps!.lon).replace(/deg|'|"/g, "").trim()
                  window.open(`https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}&zoom=15`, "_blank")
                }}>
                <MapPin className="h-3 w-3 mr-1" />
                {t("View on map", "Auf Karte zeigen")}
              </Button>
            </div>
          </div>
        )}

        <div className="mt-3 pt-3 border-t">
          <Button variant="outline" size="sm" onClick={() => {
            if (selectedFile) setQuickRename({ path: selectedFile.path, name: selectedFile.name })
          }}>
            <Pencil className="h-3 w-3 mr-1" /> {t("Quick Rename", "Schnell umbenennen")}
          </Button>
          {quickRename && (
            <div className="mt-2 flex gap-1">
              <Input
                value={quickRename.name}
                onChange={e => setQuickRename(prev => prev ? {...prev, name: e.target.value} : null)}
                className="text-xs h-7"
                onKeyDown={async e => {
                  if (e.key === "Enter" && quickRename) {
                    await fileRename(quickRename.path, quickRename.name)
                    setQuickRename(null)
                    toast("success", t("Renamed", "Umbenannt"))
                    const next = new Map(loadedPages)
                    next.delete(page)
                    setLoadedPages(next)
                    loadedPagesRef.current = next
                    loadPageData(page)
                  }
                }}
                autoFocus
              />
              <Button size="sm" className="h-7" onClick={async () => {
                if (quickRename) {
                  await fileRename(quickRename.path, quickRename.name)
                  setQuickRename(null)
                  toast("success", t("Renamed", "Umbenannt"))
                  const next = new Map(loadedPages)
                  next.delete(page)
                  setLoadedPages(next)
                  loadedPagesRef.current = next
                  loadPageData(page)
                }
              }}>{t("OK", "OK")}</Button>
              <Button variant="ghost" size="sm" className="h-7" onClick={() => setQuickRename(null)}>
                {t("Cancel", "Abbrechen")}
              </Button>
            </div>
          )}
        </div>
      </div>
    )}

      {/* Batch action bar */}
      {selectMode && selectedPaths.size > 0 && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-background border shadow-lg rounded-lg px-4 py-2 flex items-center gap-3 z-40">
          <span className="text-sm font-medium">{selectedPaths.size} {t("selected", "ausgewählt")}</span>

          <Button variant="destructive" size="sm" onClick={async () => {
            if (!confirm(t(`Delete ${selectedPaths.size} files?`, `${selectedPaths.size} Dateien löschen?`))) return
            for (const path of selectedPaths) {
              try { await fileDelete(path) } catch (e) { console.error(e) }
            }
            toast("success", t(`Deleted ${selectedPaths.size} files`, `${selectedPaths.size} Dateien gelöscht`))
            setSelectedPaths(new Set())
            loadPageData(page)
          }}>
            <Trash2 className="h-3 w-3 mr-1" /> {t("Delete selected", "Auswahl löschen")}
          </Button>

          <Input value={batchTagInput} onChange={e => setBatchTagInput(e.target.value)}
            placeholder={t("Add tag to selected...", "Tag zu Auswahl hinzufügen...")}
            className="text-xs w-40"
            onKeyDown={e => {
              if (e.key === "Enter" && batchTagInput.trim()) {
                const tag = batchTagInput.trim().toLowerCase()
                const newTags = {...fileTags}
                selectedPaths.forEach(p => {
                  if (!newTags[p]) newTags[p] = []
                  if (!newTags[p].includes(tag)) newTags[p] = [...newTags[p], tag]
                })
                setFileTags(newTags)
                localStorage.setItem("library_file_tags", JSON.stringify(newTags))
                const tagSet = new Set<string>()
                Object.values(newTags).forEach(ts => ts.forEach(t => tagSet.add(t)))
                setAllTags(Array.from(tagSet).sort())
                localStorage.setItem("library_tags", JSON.stringify(Array.from(tagSet).sort()))
                setBatchTagInput("")
                toast("success", t("Tag added", "Tag hinzugefügt"))
              }
            }} />

          <StarRating value={0} size="sm" onChange={(v) => {
            const newRatings = {...ratings}
            selectedPaths.forEach(p => { newRatings[p] = v })
            setRatings(newRatings)
            localStorage.setItem("library_ratings", JSON.stringify(newRatings))
          }} />

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

          <Button size="sm" variant="outline" onClick={async () => {
            toast("info", t(`Exporting ${selectedPaths.size} files...`, `Exportiere ${selectedPaths.size} Dateien...`))
            const paths = Array.from(selectedPaths)
            for (const path of paths) {
              const outPath = path.replace(/\.[^.]+$/, "_export.jpg")
              try { await fileExport(path, outPath, 2048, 85) } catch {}
            }
            toast("success", t("Export complete", "Export abgeschlossen"))
          }}>
            <Download className="h-3 w-3 mr-1" /> {t("Export selected", "Auswahl exportieren")}
          </Button>

          <Button variant="outline" size="sm" onClick={() => {
            navigate("/organize", { state: { preselectedFiles: Array.from(selectedPaths) } })
          }}>
            <FolderSync className="h-3 w-3 mr-1" /> {t("Organize selected", "Auswahl organisieren")}
          </Button>

          <Button size="sm" variant="outline" onClick={() => setSelectedPaths(new Set())}>
            {t("Clear", "Löschen")}
          </Button>
        </div>
      )}

      {/* Empty states */}
      {!loading && data && !loadingPages.has(page) && sortedFiles.length === 0 && (
        <EmptyState
          icon={FolderSearch}
          title={filter ? t("No matches", "Keine Treffer") : t("No files found", "Keine Dateien gefunden")}
          description={filter ? t("Try a different filter.", "Anderen Filter versuchen.") : t("The directory is empty.", "Das Verzeichnis ist leer.")}
        />
      )}

      {!data && !loading && (
        <EmptyState
          icon={FolderOpen}
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
            <Button variant="outline" size="sm" onClick={() => setDeleteDialog(null)}>
              {t("Cancel", "Abbrechen")}
            </Button>
            <Button variant="destructive" size="sm" onClick={handleDeleteConfirm}>
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
            <Button variant="outline" size="sm" onClick={() => setRenameDialog(null)}>
              {t("Cancel", "Abbrechen")}
            </Button>
            <Button variant="default" size="sm" onClick={handleRenameConfirm} disabled={!renameValue.trim() || renameValue === renameDialog?.name}>
              {t("Rename", "Umbenennen")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Slideshow */}
      {slideshowOpen && (
        <Suspense fallback={<div className="fixed inset-0 z-50 bg-background flex items-center justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>}>
        <Slideshow
          files={slideshowFiles}
          onClose={() => setSlideshowOpen(false)}
        />
        </Suspense>
      )}

      {/* Split View */}
      {splitViewOpen && (
        <SplitView
          files={splitViewFiles}
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
      </main>
    </>
  )
}
