import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Download } from "lucide-react"

interface ExportDialogProps {
  open: boolean
  onOpenChange: (v: boolean) => void
  filePath: string
  fileName: string
}

export function ExportDialog({ open, onOpenChange, filePath, fileName }: ExportDialogProps) {
  const t = useT()
  const [width, setWidth] = useState("2048")
  const [quality, setQuality] = useState("85")
  const [exporting, setExporting] = useState(false)

  const handleExport = async () => {
    setExporting(true)
    try {
      const { save } = await import("@tauri-apps/plugin-dialog")
      const path = await save({
        defaultPath: fileName.replace(/\.[^.]+$/, "_exported.jpg"),
        filters: [{ name: "JPEG", extensions: ["jpg", "jpeg"] }],
      })
      if (!path) return

      const { fileExport } = await import("@/lib/tauri-bridge")
      await fileExport(filePath, path, parseInt(width), parseInt(quality))
    } catch (e) { console.error(e) }
    finally { setExporting(false); onOpenChange(false) }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>{t("Export Image", "Bild exportieren")}</DialogTitle>
          <DialogDescription>
            {fileName}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-muted-foreground">{t("Max width (px)", "Max. Breite (px)")}</label>
            <Input value={width} onChange={e => setWidth(e.target.value)} type="number" className="text-xs" />
          </div>
          <div>
            <label className="text-xs text-muted-foreground">{t("Quality (1-100)", "Qualität (1-100)")}</label>
            <Input value={quality} onChange={e => setQuality(e.target.value)} type="number" min="1" max="100" className="text-xs" />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {t("Cancel", "Abbrechen")}
          </Button>
          <Button onClick={handleExport} disabled={exporting}>
            <Download className="h-3 w-3 mr-1" />
            {exporting ? t("Exporting...", "Exportiere...") : t("Export", "Exportieren")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
