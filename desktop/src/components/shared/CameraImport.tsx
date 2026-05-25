import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Loader2, Camera, HardDrive } from "lucide-react"

export function CameraImport() {
  const t = useT()
  const [scanning, setScanning] = useState(false)
  const [sources, setSources] = useState<string[]>([])
  const [targetDir, setTargetDir] = useState(() => localStorage.getItem("default_source_dir") || "")
  const [importing] = useState(false)

  const scanDrives = async () => {
    setScanning(true)
    setSources([])
    try {
      const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
      const result = await libraryBrowsePaginated({
        root_dir: "D:\\DCIM",
        page: 0,
        page_size: 1,
        max_depth: 1,
      }).catch(() => null)
      if (result && result.file_count > 0) {
        setSources(prev => [...prev, "D:\\DCIM"])
      }
    } catch { /* drive not available */ }

    for (const letter of ["E", "F", "G"]) {
      try {
        const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
        const r = await libraryBrowsePaginated({
          root_dir: `${letter}:\\DCIM`,
          page: 0, page_size: 1, max_depth: 1,
        }).catch(() => null)
        if (r && r.file_count > 0) {
          setSources(prev => [...prev, `${letter}:\\DCIM`])
        }
      } catch {}
    }
    setScanning(false)
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
              <div key={s} className="flex items-center gap-2 text-xs">
                <Camera className="h-3 w-3 text-green-500" />
                <code className="bg-muted px-1 rounded">{s}</code>
              </div>
            ))}
            <div className="flex gap-2 mt-2">
              <Input value={targetDir} onChange={e => setTargetDir(e.target.value)}
                placeholder={t("Target directory", "Zielverzeichnis")} className="text-xs" />
              <Button size="sm" disabled={!targetDir || importing}>
                {t("Import", "Importieren")}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
