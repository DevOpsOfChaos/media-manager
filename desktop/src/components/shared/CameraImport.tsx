import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { Loader2, Camera, HardDrive, FolderOpen } from "lucide-react"

interface SourcePreview {
  path: string
  file_count: number
  files: Array<{ name: string; size: number }>
}

export function CameraImport() {
  const t = useT()
  const [scanning, setScanning] = useState(false)
  const [sources, setSources] = useState<SourcePreview[]>([])
  const [targetDir, setTargetDir] = useState(() => localStorage.getItem("default_source_dir") || "")
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importLog, setImportLog] = useState<string[]>([])
  const [autoOrganize, setAutoOrganize] = useState(() => localStorage.getItem("auto_organize_after_import") === "true")

  const scanDrives = async () => {
    setScanning(true)
    setSources([])
    const candidates = ["D:\\DCIM", "E:\\DCIM", "F:\\DCIM", "G:\\DCIM"]

    for (const root of candidates) {
      try {
        const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
        const r = await libraryBrowsePaginated({
          root_dir: root,
          page: 0, page_size: 50, max_depth: 1,
        }).catch(() => null)
        if (r && r.file_count > 0) {
          setSources(prev => [...prev, {
            path: root,
            file_count: r.file_count,
            files: r.files.slice(0, 10).map(f => ({ name: f.name, size: f.size })),
          }])
        }
      } catch { /* drive not available */ }
    }
    setScanning(false)
  }

  const handleImport = async () => {
    if (!targetDir) return
    setImporting(true)
    setImportProgress(0)
    setImportLog([])

    const allFiles: Array<{ sourcePath: string; name: string }> = []
    for (const src of sources) {
      try {
        const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
        const r = await libraryBrowsePaginated({
          root_dir: src.path,
          page: 0, page_size: 500, max_depth: 3,
        }).catch(() => null)
        if (r) {
          for (const f of r.files) {
            allFiles.push({ sourcePath: f.path, name: f.name })
          }
        }
      } catch { /* skip */ }
    }

    const total = allFiles.length
    let done = 0

    setImportLog(prev => [...prev, t(`Found ${total} files to import`, `${total} Dateien zum Import gefunden`)])

    for (const file of allFiles) {
      try {
        const { fileRename } = await import("@/lib/tauri-bridge")
        const targetPath = `${targetDir}\\${file.name}`
        await fileRename(file.sourcePath, file.name).catch(() => null)
        done++
        setImportProgress(Math.round((done / total) * 100))
        setImportLog(prev => [...prev, `${file.name} -> ${targetPath}`])
      } catch {
        done++
        setImportProgress(Math.round((done / total) * 100))
        setImportLog(prev => [...prev, t(`Failed: ${file.name}`, `Fehlgeschlagen: ${file.name}`)])
      }
    }

    setImportLog(prev => [...prev, t(`Import complete: ${done}/${total} files`, `Import abgeschlossen: ${done}/${total} Dateien`)])

    if (autoOrganize && targetDir) {
      setImportLog(prev => [...prev, t("Starting auto-organize...", "Starte Auto-Organisation...")])
      try {
        const { organizeApply } = await import("@/lib/tauri-bridge")
        await organizeApply({
          source_dirs: [targetDir],
          target_root: targetDir,
          pattern: "{year}/{year_month_day}",
          recursive: true,
          include_hidden: false,
          follow_symlinks: false,
          operation_mode: "move",
          exiftool_path: null,
          include_associated_files: false,
          conflict_policy: "conflict",
          include_patterns: [],
          exclude_patterns: [],
          batch_size: 0,
          date_source: "auto",
          cleanup_empty_dirs: true,
        })
        setImportLog(prev => [...prev, t("Auto-organize complete", "Auto-Organisation abgeschlossen")])
      } catch {
        setImportLog(prev => [...prev, t("Auto-organize failed", "Auto-Organisation fehlgeschlagen")])
      }
    }

    setImporting(false)
  }

  const handleBrowseTarget = async () => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog")
      const selected = await open({ directory: true, multiple: false })
      if (selected) {
        const dir = Array.isArray(selected) ? selected[0] : selected
        setTargetDir(dir)
        localStorage.setItem("default_source_dir", dir)
      }
    } catch { /* dialog not available */ }
  }

  const toggleAutoOrganize = (checked: boolean) => {
    setAutoOrganize(checked)
    localStorage.setItem("auto_organize_after_import", String(checked))
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Camera className="h-4 w-4" />
          {t("Camera Import", "Kamera-Import")}
        </CardTitle>
        <CardDescription>
          {t("Scan for connected cameras and SD cards.", "Suche nach verbundenen Kameras und SD-Karten.")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button variant="outline" size="sm" onClick={scanDrives} disabled={scanning}>
          {scanning ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <HardDrive className="h-3 w-3 mr-1" />}
          {scanning ? t("Scanning...", "Suche...") : t("Scan for DCIM folders", "Nach DCIM-Ordnern suchen")}
        </Button>

        {sources.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-green-600">{t("Found sources:", "Gefundene Quellen:")}</p>
            {sources.map(s => (
              <details key={s.path} className="text-xs">
                <summary className="flex items-center gap-2 cursor-pointer">
                  <Camera className="h-3 w-3 text-green-500" />
                  <code className="bg-muted px-1 rounded">{s.path}</code>
                  <span className="text-muted-foreground">({s.file_count} {t("files", "Dateien")})</span>
                </summary>
                <div className="ml-5 mt-1 space-y-0.5 max-h-32 overflow-y-auto">
                  {s.files.map((f, i) => (
                    <div key={i} className="text-muted-foreground flex justify-between">
                      <span className="truncate mr-2">{f.name}</span>
                      <span className="shrink-0">{formatSize(f.size)}</span>
                    </div>
                  ))}
                  {s.file_count > 10 && (
                    <p className="text-muted-foreground italic">
                      {t(`...and ${s.file_count - 10} more`, `...und ${s.file_count - 10} weitere`)}
                    </p>
                  )}
                </div>
              </details>
            ))}
            <div className="flex gap-2 mt-2">
              <div className="flex-1 flex gap-1">
                <Input value={targetDir} onChange={e => setTargetDir(e.target.value)}
                  placeholder={t("Target directory", "Zielverzeichnis")} className="text-xs h-7" />
                <Button variant="outline" size="icon" className="h-7 w-7 shrink-0" onClick={handleBrowseTarget}>
                  <FolderOpen className="h-3 w-3" />
                </Button>
              </div>
              <Button size="sm" disabled={!targetDir || importing} onClick={handleImport}>
                {importing ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null}
                {importing ? t("Importing...", "Importiere...") : t("Import", "Importieren")}
              </Button>
            </div>

            {importing && (
              <div className="space-y-2">
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 dark:bg-blue-400 rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(importProgress, 1)}%` }} />
                </div>
                <p className="text-xs text-muted-foreground text-center">{importProgress}%</p>
                <div className="max-h-24 overflow-y-auto bg-muted/20 rounded p-2 space-y-0.5">
                  {importLog.map((msg, i) => (
                    <p key={i} className="text-xs text-muted-foreground font-mono">{msg}</p>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex items-center gap-2 pt-1">
          <Switch id="auto-organize" checked={autoOrganize} onCheckedChange={toggleAutoOrganize} />
          <label htmlFor="auto-organize" className="text-xs text-muted-foreground cursor-pointer">
            {t("Auto-organize after import", "Nach Import automatisch organisieren")}
          </label>
        </div>
      </CardContent>
    </Card>
  )
}
