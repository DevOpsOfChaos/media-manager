import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Eye, RefreshCw } from "lucide-react"

interface WatchdogIndicatorProps {
  rootDir: string
  onRescan: () => void
}

export function WatchdogIndicator({ rootDir, onRescan }: WatchdogIndicatorProps) {
  const t = useT()
  const [lastScan, setLastScan] = useState<string | null>(() => localStorage.getItem(`last_scan_${rootDir}`))

  useEffect(() => {
    if (rootDir) {
      localStorage.setItem(`last_scan_${rootDir}`, new Date().toISOString())
      setLastScan(new Date().toISOString())
    }
  }, [rootDir])

  return (
    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
      <Eye className="h-3 w-3" />
      {lastScan ? (
        <span>{t(`Last scan: ${new Date(lastScan).toLocaleTimeString()}`, `Letzter Scan: ${new Date(lastScan).toLocaleTimeString()}`)}</span>
      ) : (
        <span>{t("Not scanned yet", "Noch nicht gescannt")}</span>
      )}
      <Button variant="ghost" size="sm" className="h-5 text-[10px]" onClick={onRescan}>
        <RefreshCw className="h-2.5 w-2.5 mr-0.5" /> {t("Refresh", "Aktualisieren")}
      </Button>
    </div>
  )
}
