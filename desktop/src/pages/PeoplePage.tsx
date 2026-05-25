import { useState, useCallback, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { peopleScan, peopleScanStatus, peopleScanReset, peopleCatalogInfo, type PeopleScanResult, type PeopleScanStatus, type CatalogInfo } from "@/lib/tauri-bridge"
import { EmptyState } from "@/components/shared/EmptyState"
import { useSettingsStore } from "@/stores/settings-store"
import { Users, ScanFace, Loader2, CheckCircle2, Clock, Shield, Trash2 } from "lucide-react"

export default function PeoplePage() {
  const [sourceDir, setSourceDir] = useState("")
  const [catalogPath, setCatalogPath] = useState("")
  const [enabled, setEnabled] = useState(false)
  const [loading, setLoading] = useState(false)
  const [scanResult, setScanResult] = useState<PeopleScanResult | null>(null)
  const [scanStatus, setScanStatus] = useState<PeopleScanStatus | null>(null)
  const [catalogInfo, setCatalogInfo] = useState<CatalogInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastScanTime, setLastScanTime] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  useSettingsStore()

  // Load saved state on mount
  useEffect(() => {
    const stored = localStorage.getItem("people_scan_enabled")
    if (stored === "true") setEnabled(true)
    const storedSource = localStorage.getItem("people_scan_source")
    if (storedSource) setSourceDir(storedSource)
    const storedCatalog = localStorage.getItem("people_scan_catalog")
    if (storedCatalog) setCatalogPath(storedCatalog)
  }, [])

  // Check scan status when enabled
  useEffect(() => {
    if (!enabled || !sourceDir) return
    const check = async () => {
      try {
        const status = await peopleScanStatus({ source_dirs: [sourceDir] })
        setScanStatus(status)
      } catch { /* ignore */ }
    }
    check()
  }, [enabled, sourceDir])

  // Auto-rescan polling
  useEffect(() => {
    if (pollingRef.current) clearInterval(pollingRef.current)
    if (!enabled || !sourceDir) return

    pollingRef.current = setInterval(async () => {
      try {
        const result = await peopleScan({
          source_dirs: [sourceDir],
          catalog_path: catalogPath || undefined,
          incremental: true,
          tolerance: 0.6,
        })
        setScanResult(result)
        setLastScanTime(new Date().toLocaleTimeString())
        // Update status too
        const status = await peopleScanStatus({ source_dirs: [sourceDir] })
        setScanStatus(status)
      } catch { /* silent poll failure */ }
    }, 30000) // every 30 seconds

    return () => { if (pollingRef.current) clearInterval(pollingRef.current) }
  }, [enabled, sourceDir, catalogPath])

  const handleToggle = (checked: boolean) => {
    setEnabled(checked)
    localStorage.setItem("people_scan_enabled", String(checked))
    if (!checked) {
      if (pollingRef.current) clearInterval(pollingRef.current)
      return
    }
    // Save state when enabling
    localStorage.setItem("people_scan_source", sourceDir)
    localStorage.setItem("people_scan_catalog", catalogPath)
    // Trigger initial scan
    handleFullScan()
  }

  const handleFullScan = useCallback(async () => {
    if (!sourceDir) return
    setLoading(true); setError(null)
    try {
      localStorage.setItem("people_scan_source", sourceDir)
      localStorage.setItem("people_scan_catalog", catalogPath)
      const result = await peopleScan({
        source_dirs: [sourceDir],
        catalog_path: catalogPath || undefined,
        incremental: false,
        force_full: true,
        tolerance: 0.6,
      })
      setScanResult(result)
      setLastScanTime(new Date().toLocaleTimeString())
      const status = await peopleScanStatus({ source_dirs: [sourceDir] })
      setScanStatus(status)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }, [sourceDir, catalogPath])

  const handleReset = useCallback(async () => {
    if (!sourceDir) return
    try {
      await peopleScanReset({ source_dirs: [sourceDir] })
      setScanResult(null)
      setScanStatus(null)
      setLastScanTime(null)
    } catch (e) { setError(String(e)) }
  }, [sourceDir])

  const handleCatalogInfo = useCallback(async () => {
    if (!catalogPath) return
    try {
      const info = await peopleCatalogInfo({ catalog_path: catalogPath })
      setCatalogInfo(info)
    } catch (e) { setError(String(e)) }
  }, [catalogPath])

  const scannedPercent = scanResult && scanResult.total_files > 0
    ? Math.round((scanResult.scanned_files / scanResult.total_files) * 100)
    : 0

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-primary" />
          <div>
            <h1 className="text-xl font-bold">People & Faces</h1>
            <p className="text-sm text-muted-foreground">Smart face detection with automatic rescanning.</p>
          </div>
        </div>
      </div>

      {/* Privacy & Enable Toggle */}
      <Card className={enabled ? "border-green-500/30" : ""}>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center justify-between">
            <span className="flex items-center gap-2"><Shield className="w-4 h-4" /> Face Recognition</span>
            <Switch checked={enabled} onCheckedChange={handleToggle} />
          </CardTitle>
        </CardHeader>
        {enabled && (
          <CardContent className="space-y-3 pt-0">
            <p className="text-xs text-muted-foreground">
              Face recognition is active. Photos are scanned incrementally — only new or changed files are processed.
              Scans resume automatically every 30 seconds.
            </p>
          </CardContent>
        )}
        {!enabled && (
          <CardContent className="pt-0">
            <p className="text-xs text-muted-foreground">
              Face recognition is disabled. Enable it to scan photos for faces and match against your people catalog.
              Your privacy is respected — all data stays on your device.
            </p>
          </CardContent>
        )}
      </Card>

      {enabled && (
        <>
          {/* Configuration */}
          <Card>
            <CardHeader><CardTitle className="text-base">Scan Configuration</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium">Source Directory</label>
                <Input value={sourceDir} onChange={e => setSourceDir(e.target.value)} placeholder="C:\Photos" className="text-xs" disabled={loading} />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium">People Catalog (optional)</label>
                <div className="flex gap-2">
                  <Input value={catalogPath} onChange={e => setCatalogPath(e.target.value)} placeholder="catalog.json" className="text-xs flex-1" disabled={loading} />
                  <Button onClick={handleCatalogInfo} variant="outline" size="sm" disabled={!catalogPath}>Info</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Scan Controls */}
          <div className="flex gap-2">
            <Button onClick={handleFullScan} disabled={loading || !sourceDir} size="sm">
              {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Scanning...</> : <><ScanFace className="w-4 h-4 mr-2" /> Full Scan Now</>}
            </Button>
            <Button onClick={handleReset} variant="ghost" size="sm" disabled={loading}>
              <Trash2 className="w-4 h-4 mr-1" /> Reset Cache
            </Button>
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          {/* Scan Status */}
          {scanStatus && (
            <Card className="border-blue-500/20 bg-blue-500/5">
              <CardContent className="py-3">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <span>
                      {scanStatus.has_cache
                        ? `${scanStatus.cached_files} files cached`
                        : "No scan cache yet"}
                    </span>
                  </div>
                  {lastScanTime && (
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" /> Last scan: {lastScanTime}
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Scan Results */}
          {scanResult && (
            <Card className="border-blue-500/30">
              <CardHeader>
                <CardTitle className="text-sm flex items-center justify-between">
                  <span>Scan Results</span>
                  <Badge variant="outline" className="text-xs">
                    {scanResult.incremental ? "Incremental" : "Full"} · {scannedPercent}% scanned
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="p-3 rounded bg-muted/30">
                    <p className="text-xl font-bold">{scanResult.total_faces}</p>
                    <p className="text-[10px] text-muted-foreground">Total Faces</p>
                  </div>
                  <div className="p-3 rounded bg-green-500/10">
                    <p className="text-xl font-bold text-green-400">{scanResult.matched_faces}</p>
                    <p className="text-[10px] text-muted-foreground">Matched</p>
                  </div>
                  <div className="p-3 rounded bg-yellow-500/10">
                    <p className="text-xl font-bold text-yellow-400">{scanResult.unknown_faces}</p>
                    <p className="text-[10px] text-muted-foreground">Unknown</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mt-3">
                  <Badge variant="secondary">{scanResult.people_count} people</Badge>
                  <Badge variant="secondary">{scanResult.image_count} images</Badge>
                  <Badge variant="outline">{scanResult.scanned_files} scanned</Badge>
                  <Badge variant="outline">{scanResult.skipped_files} skipped</Badge>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Catalog Info */}
          {catalogInfo && (
            <Card className="border-green-500/30">
              <CardHeader><CardTitle className="text-sm">Catalog: {catalogInfo.path.split("/").pop()?.split("\\").pop()}</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-2">{catalogInfo.person_count} people</p>
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {catalogInfo.people.slice(0, 15).map(p => (
                    <div key={p.person_id} className="flex justify-between text-xs py-1 border-b border-border/30">
                      <span>{p.name}</span>
                      <span className="text-muted-foreground">{p.face_count} faces</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {!enabled && (
        <EmptyState
          title="Face Recognition is Off"
          description="Toggle the switch above to enable face detection. Your photos stay on your device — nothing is uploaded or shared."
        />
      )}
    </div>
  )
}
