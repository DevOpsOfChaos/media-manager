import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { peopleScan, peopleCatalogInfo, type PeopleScanResult, type CatalogInfo } from "@/lib/tauri-bridge"
import { EmptyState } from "@/components/shared/EmptyState"
import { PreflightCheck } from "@/components/shared/PreflightCheck"
import { Users, ScanFace, BookUser, Loader2 } from "lucide-react"

export default function PeoplePage() {
  const [sourceDir, setSourceDir] = useState("")
  const [catalogPath, setCatalogPath] = useState("")
  const [loading, setLoading] = useState(false)
  const [scanResult, setScanResult] = useState<PeopleScanResult | null>(null)
  const [catalogInfo, setCatalogInfo] = useState<CatalogInfo | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleScan = useCallback(async () => {
    if (!sourceDir) return
    setLoading(true); setError(null)
    try {
      const result = await peopleScan({
        source_dirs: [sourceDir],
        catalog_path: catalogPath || undefined,
        tolerance: 0.6,
      })
      setScanResult(result)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }, [sourceDir, catalogPath])

  const handleCatalogInfo = useCallback(async () => {
    if (!catalogPath) return
    setLoading(true); setError(null)
    try {
      const info = await peopleCatalogInfo({ catalog_path: catalogPath })
      setCatalogInfo(info)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }, [catalogPath])

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Users className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-xl font-bold">People & Faces</h1>
          <p className="text-sm text-muted-foreground">Scan photos for faces and match against a people catalog.</p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base flex items-center gap-2"><ScanFace className="w-4 h-4" /> Face Scan</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <Input value={sourceDir} onChange={e => setSourceDir(e.target.value)} placeholder="Source directory" className="text-xs" disabled={loading} />
          <Input value={catalogPath} onChange={e => setCatalogPath(e.target.value)} placeholder="Catalog path (optional JSON)" className="text-xs" disabled={loading} />
          <div className="flex gap-2">
            <Button onClick={handleScan} disabled={loading || !sourceDir} size="sm">
              {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Scanning...</> : "Scan for Faces"}
            </Button>
            <Button onClick={handleCatalogInfo} disabled={loading || !catalogPath} variant="outline" size="sm">
              <BookUser className="w-4 h-4 mr-1" /> Catalog Info
            </Button>
          </div>
        </CardContent>
      </Card>

      <PreflightCheck sourceDirs={sourceDir ? [sourceDir] : []} command="people" />

      {error && <p className="text-sm text-red-400">{error}</p>}

      {scanResult && (
        <Card className="border-blue-500/30">
          <CardHeader><CardTitle className="text-sm">Scan Results</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{scanResult.total_faces} faces</Badge>
              <Badge variant="outline">{scanResult.matched_faces} matched</Badge>
              <Badge variant="secondary">{scanResult.unknown_faces} unknown</Badge>
              <Badge variant="outline">{scanResult.people_count} people</Badge>
              <Badge variant="outline">{scanResult.image_count} images</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {catalogInfo && (
        <Card className="border-green-500/30">
          <CardHeader><CardTitle className="text-sm">Catalog: {catalogInfo.path}</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-2">{catalogInfo.person_count} people in catalog</p>
            <div className="space-y-1">
              {catalogInfo.people.slice(0, 10).map(p => (
                <div key={p.person_id} className="flex justify-between text-xs">
                  <span>{p.name}</span>
                  <span className="text-muted-foreground">{p.face_count} faces</span>
                </div>
              ))}
              {catalogInfo.people.length > 10 && (
                <p className="text-xs text-muted-foreground">+{catalogInfo.people.length - 10} more</p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {!scanResult && !catalogInfo && !loading && (
        <EmptyState title="No scan data" description="Enter a source directory and optional catalog path, then click Scan for Faces." />
      )}
    </div>
  )
}
