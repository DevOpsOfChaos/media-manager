import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Mail } from "lucide-react"

interface EmailShareProps {
  selectedPaths: string[]
  onClose?: () => void
}

export function EmailShare({ selectedPaths, onClose }: EmailShareProps) {
  const t = useT()

  const handleEmailShare = async () => {
    try {
      const { openUrl } = await import("@tauri-apps/plugin-opener")
      const subject = encodeURIComponent(t("Shared from Media Manager", "Geteilt von Media Manager"))
      const body = encodeURIComponent(
        selectedPaths.map(p => p.split("/").pop() || p.split("\\").pop()).join(", ") +
        "\n\n" + t("These photos were selected in Media Manager.", "Diese Fotos wurden in Media Manager ausgewählt.")
      )
      openUrl(`mailto:?subject=${subject}&body=${body}`)
    } catch {
      const list = selectedPaths.map(p => p.split("/").pop() || p.split("\\").pop()).join("\n")
      await navigator.clipboard.writeText(list)
      alert(t("File list copied to clipboard. Paste into your email client.",
              "Dateiliste in Zwischenablage kopiert. In E-Mail-Client einfügen."))
    }
    onClose?.()
  }

  const handleResizeAndShare = async () => {
    try {
      const { fileExport } = await import("@/lib/tauri-bridge")
      const exportedPaths: string[] = []
      for (const path of selectedPaths.slice(0, 10)) {
        const outPath = path.replace(/\.[^.]+$/, "_shared.jpg")
        try {
          await fileExport(path, outPath, 1200, 80)
          exportedPaths.push(outPath)
        } catch {}
      }
      const { openUrl } = await import("@tauri-apps/plugin-opener")
      const subject = encodeURIComponent(t("Shared photos from Media Manager", "Geteilte Fotos von Media Manager"))
      const body = encodeURIComponent(t("Resized photos attached.", "Verkleinerte Fotos angehängt."))
      openUrl(`mailto:?subject=${subject}&body=${body}`)
    } catch (e) {
      console.error(e)
    }
    onClose?.()
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Mail className="h-4 w-4" />
          {t("Share via Email", "Per E-Mail teilen")}
        </CardTitle>
        <CardDescription>
          {selectedPaths.length === 1
            ? t("Share 1 photo", "1 Foto teilen")
            : t(`Share ${selectedPaths.length} photos`, `${selectedPaths.length} Fotos teilen`)}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button size="sm" variant="outline" onClick={handleEmailShare} className="text-xs">
          <Mail className="h-3 w-3 mr-1" /> {t("Open Email Client", "E-Mail-Client öffnen")}
        </Button>
        <Button size="sm" variant="outline" onClick={handleResizeAndShare} className="text-xs">
          <Mail className="h-3 w-3 mr-1" /> {t("Resize & Email (max 1200px)", "Verkleinern & E-Mail (max. 1200px)")}
        </Button>
        <p className="text-[10px] text-muted-foreground">
          {t("Opens your default email client with file names.", "Öffnet den Standard-E-Mail-Client mit Dateinamen.")}
        </p>
      </CardContent>
    </Card>
  )
}
