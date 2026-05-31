import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { FolderOpen, Smartphone, Camera, HardDrive, Clock } from "lucide-react"
import type { LibraryBrowsePaginatedResult } from "@/lib/tauri-bridge"

interface DetectedSource {
  type: "device" | "recent" | "favorite"
  label: string
  path: string
  info?: string
  icon: "phone" | "camera" | "drive" | "folder"
}

interface SourceDetectorProps {
  value: string
  onChange: (path: string) => void
  targetValue?: string
  onTargetChange?: (path: string) => void
  showTarget?: boolean
}

function saveRecent(path: string) {
  try {
    const recent: string[] = JSON.parse(localStorage.getItem("recent_source_dirs") || "[]")
    const filtered = recent.filter((p: string) => p !== path)
    filtered.unshift(path)
    localStorage.setItem("recent_source_dirs", JSON.stringify(filtered.slice(0, 5)))
  } catch {}
}

export function SourceDetector({ value, onChange, targetValue, onTargetChange, showTarget = true }: SourceDetectorProps) {
  const t = useT()
  const [sources, setSources] = useState<DetectedSource[]>([])
  const [scanning, setScanning] = useState(false)

  useEffect(() => {
    loadSuggestions()
  }, [])

  const loadSuggestions = async () => {
    setScanning(true)
    const items: DetectedSource[] = []

    try {
      const recent: string[] = JSON.parse(localStorage.getItem("recent_source_dirs") || "[]")
      for (const dir of recent.slice(0, 3)) {
        items.push({
          type: "recent", label: dir.split(/[\\/]/).pop() || dir,
          path: dir, info: t("Recently used", "Kürzlich genutzt"), icon: "folder"
        })
      }
    } catch {}

    try {
      const fav: Record<string, boolean> = JSON.parse(localStorage.getItem("sidebar_favorites") || "{}")
      if (fav.organize) {
        items.push({
          type: "favorite", label: "Organize Favorite", path: "", info: "", icon: "folder"
        })
      }
    } catch {}

    try {
      const drives = ['D:\\', 'E:\\', 'F:\\', 'G:\\']
      for (const drive of drives) {
        try {
          const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
          const r: LibraryBrowsePaginatedResult | null = await libraryBrowsePaginated({
            root_dir: drive + 'DCIM',
            page: 0, page_size: 1, max_depth: 1,
          }).catch(() => null)
          if (r && r.file_count > 0) {
            items.push({
              type: "device",
              label: `DCIM (${drive})`,
              path: drive + 'DCIM',
              info: `${r.file_count} ${t("files", "Dateien")}`,
              icon: "camera"
            })
          }
        } catch {}
      }
    } catch {}

    setSources(items)
    setScanning(false)
  }

  const browseFolder = async (target: "source" | "target") => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog")
      const selected = await open({ directory: true })
      if (selected && typeof selected === "string") {
        if (target === "source") onChange(selected)
        else onTargetChange?.(selected)
      }
    } catch {}
  }

  const iconMap = { phone: Smartphone, camera: Camera, drive: HardDrive, folder: FolderOpen }

  return (
    <div className="space-y-4">
      {sources.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground">{t("Suggested sources", "Vorgeschlagene Quellen")}</p>
          <div className="space-y-1">
            {sources.map((s, i) => {
              const Icon = iconMap[s.icon]
              return (
                <button key={i} onClick={() => { onChange(s.path); saveRecent(s.path) }}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg border text-left transition-colors ${
                    value === s.path ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/30'
                  }`}>
                  <Icon className="h-5 w-5 text-muted-foreground shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{s.label}</p>
                    <p className="text-[10px] text-muted-foreground">{s.path} {s.info && `· ${s.info}`}</p>
                  </div>
                  {value === s.path && <div className="w-3 h-3 rounded-full bg-primary shrink-0" />}
                </button>
              )
            })}
          </div>
          <button onClick={loadSuggestions} className="text-[10px] text-muted-foreground hover:text-foreground">
            <Clock className="h-3 w-3 inline mr-1" /> {scanning ? t("Scanning...", "Suche...") : t("Refresh", "Aktualisieren")}
          </button>
        </div>
      )}

      <div className="space-y-2">
        <label className="text-sm font-medium">{t("Source directory", "Quellverzeichnis")}</label>
        <div className="flex gap-2">
          <Input value={value} onChange={e => onChange(e.target.value)} placeholder="G:\Bilder_unsortiert" className="text-sm" />
          <Button variant="outline" size="icon" onClick={() => browseFolder("source")}><FolderOpen className="h-4 w-4" /></Button>
        </div>
      </div>

      {showTarget && (
        <div className="space-y-2">
          <label className="text-sm font-medium">{t("Target directory", "Zielverzeichnis")}</label>
          <div className="flex gap-2">
            <Input value={targetValue || ""} onChange={e => onTargetChange?.(e.target.value)}
              placeholder={localStorage.getItem("default_source_dir") || "G:\Medienspeicher"} className="text-sm" />
            <Button variant="outline" size="icon" onClick={() => browseFolder("target")}><FolderOpen className="h-4 w-4" /></Button>
          </div>
        </div>
      )}
    </div>
  )
}
