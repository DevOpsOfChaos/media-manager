import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

import { Badge } from "@/components/ui/badge"
import { tripPreview, tripApply, type TripPreviewResponse, type TripApplyResponse } from "@/lib/tauri-bridge"
import { PreflightCheck } from "@/components/shared/PreflightCheck"
import { EmptyState } from "@/components/shared/EmptyState"
import { Plane, Link, Copy, Loader2 } from "lucide-react"

export default function TripPage() {
  const [sourceDir, setSourceDir] = useState("")
  const [targetDir, setTargetDir] = useState("")
  const [label, setLabel] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [useHardlinks, setUseHardlinks] = useState(true)
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState<TripPreviewResponse | null>(null)
  const [result, setResult] = useState<TripApplyResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const options = {
    source_dirs: sourceDir ? [sourceDir] : [],
    target_root: targetDir,
    label: label || "trip",
    start_date: startDate,
    end_date: endDate,
    use_hardlinks: useHardlinks,
  }

  const handlePreview = useCallback(async () => {
    if (!sourceDir || !targetDir || !startDate || !endDate) return
    setLoading(true); setError(null); setPreview(null); setResult(null)
    try {
      const p = await tripPreview(options)
      setPreview(p)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }, [sourceDir, targetDir, label, startDate, endDate, useHardlinks])

  const handleApply = useCallback(async () => {
    setLoading(true); setError(null); setResult(null)
    try {
      const r = await tripApply(options)
      setResult(r)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }, [sourceDir, targetDir, label, startDate, endDate, useHardlinks])

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Plane className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Trip Collection</h1>
          <p className="text-sm text-muted-foreground">Build a collection from a date range using hardlinks or copies.</p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Trip Settings</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <span className="text-xs font-medium">Source Directory</span>
              <Input value={sourceDir} onChange={e => setSourceDir(e.target.value)} placeholder="C:\Photos" className="text-xs" />
            </div>
            <div className="space-y-1">
              <span className="text-xs font-medium">Target Directory</span>
              <Input value={targetDir} onChange={e => setTargetDir(e.target.value)} placeholder="C:\Trips" className="text-xs" />
            </div>
          </div>
          <div className="space-y-1">
            <span className="text-xs font-medium">Trip Label</span>
            <Input value={label} onChange={e => setLabel(e.target.value)} placeholder="Italy_2025" className="text-xs" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <span className="text-xs font-medium">Start Date (YYYY-MM-DD)</span>
              <Input value={startDate} onChange={e => setStartDate(e.target.value)} placeholder="2025-06-01" className="text-xs" />
            </div>
            <div className="space-y-1">
              <span className="text-xs font-medium">End Date (YYYY-MM-DD)</span>
              <Input value={endDate} onChange={e => setEndDate(e.target.value)} placeholder="2025-06-15" className="text-xs" />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <label className="text-xs flex items-center gap-2 cursor-pointer">
              <input type="radio" checked={useHardlinks} onChange={() => setUseHardlinks(true)} />
              <Link className="w-3.5 h-3.5" /> Hardlinks (no extra space)
            </label>
            <label className="text-xs flex items-center gap-2 cursor-pointer">
              <input type="radio" checked={!useHardlinks} onChange={() => setUseHardlinks(false)} />
              <Copy className="w-3.5 h-3.5" /> Copy files
            </label>
          </div>
        </CardContent>
      </Card>

      <PreflightCheck sourceDirs={sourceDir ? [sourceDir] : []} targetRoot={targetDir} command="trip" />

      <div className="flex gap-2">
        <Button onClick={handlePreview} disabled={loading || !sourceDir || !targetDir || !startDate || !endDate} size="sm">
          {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Scanning...</> : "Preview"}
        </Button>
        {preview && preview.planned_count > 0 && (
          <Button onClick={handleApply} disabled={loading} variant="default" size="sm">
            Apply ({preview.planned_count} files)
          </Button>
        )}
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {preview && (
        <Card className="border-blue-500/30">
          <CardHeader><CardTitle className="text-sm">Trip Preview</CardTitle></CardHeader>
          <CardContent>
            <div className="flex gap-3 text-sm">
              <Badge variant="outline">{preview.matched_count} matched</Badge>
              <Badge variant="outline">{preview.planned_count} planned</Badge>
              <Badge variant="secondary">{preview.skipped_count} skipped</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card className="border-green-500/30">
          <CardHeader><CardTitle className="text-sm text-green-400">Trip Created</CardTitle></CardHeader>
          <CardContent>
            <div className="flex gap-3 text-sm">
              <Badge>{result.linked_count} linked</Badge>
              <Badge>{result.copied_count} copied</Badge>
              <Badge variant="secondary">{result.skipped_count} skipped</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {!preview && !result && !loading && (
        <EmptyState title="No trip configured" description="Set your source, target, date range and label above, then click Preview." />
      )}
    </div>
  )
}
