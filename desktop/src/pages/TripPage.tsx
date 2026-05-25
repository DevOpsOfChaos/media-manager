import { useState, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { tripPreview, tripApply, type TripOptions, type TripApplyResponse } from "@/lib/tauri-bridge"
import { libraryBrowse } from "@/lib/tauri-bridge"
import { convertFileSrc } from "@tauri-apps/api/core"
import { EmptyState } from "@/components/shared/EmptyState"
import { Plane, Plus, FolderOpen, Loader2, ImageOff, ChevronRight } from "lucide-react"

interface TripEntry {
  name: string
  path: string
  fileCount: number
  thumbnail: string | null
}

function TripDetailView({ trip, onBack }: { trip: TripEntry; onBack: () => void }) {
  const [files, setFiles] = useState<Array<{path:string;name:string;suffix:string;size:number}>>([])
  const [loadingFiles, setLoadingFiles] = useState(false)

  useEffect(() => {
    setLoadingFiles(true)
    libraryBrowse({ root_dir: trip.path }).then(r => { setFiles(r.files); setLoadingFiles(false) }).catch(() => setLoadingFiles(false))
  }, [trip.path])

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={onBack}>← Back</Button>
        <h1 className="text-xl font-bold">{trip.name}</h1>
        <Badge variant="secondary">{trip.fileCount} files</Badge>
      </div>
      {trip.thumbnail && (
        <img src={convertFileSrc(trip.thumbnail)} alt="" className="w-full max-h-48 object-cover rounded-lg" />
      )}
      {loadingFiles ? (
        <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin" /></div>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
          {files.slice(0, 200).map((f, i) => (
            <div key={i} className="aspect-square bg-muted rounded overflow-hidden">
              {[".jpg",".jpeg",".png"].includes(f.suffix) ? (
                <img src={convertFileSrc(f.path)} alt="" className="w-full h-full object-cover" loading="lazy" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground/30"><FolderOpen className="w-8 h-8" /></div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function TripPage() {
  const [tripsRoot, setTripsRoot] = useState(() => localStorage.getItem("trips_root") || "")
  const [trips, setTrips] = useState<TripEntry[]>([])
  const [loadingTrips, setLoadingTrips] = useState(false)

  // Create trip dialog
  const [showCreate, setShowCreate] = useState(false)
  const [sourceDir, setSourceDir] = useState("")
  const [label, setLabel] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [useHardlinks, setUseHardlinks] = useState(true)
  const [creating, setCreating] = useState(false)
  const [createResult, setCreateResult] = useState<TripApplyResponse | null>(null)
  const [createError, setCreateError] = useState<string | null>(null)

  // Trip detail view
  const [selectedTrip, setSelectedTrip] = useState<TripEntry | null>(null)

  const loadTrips = useCallback(async () => {
    if (!tripsRoot) return
    setLoadingTrips(true)
    try {
      const result = await libraryBrowse({ root_dir: tripsRoot, max_depth: 1 })
      // Group by top-level directories = trips
      const tripMap = new Map<string, { files: number; thumb: string | null }>()
      for (const f of result.files || []) {
        const parts = f.relative.replace(/\\/g, "/").split("/")
        const tripName = parts[0] || "unknown"
        if (!tripMap.has(tripName)) tripMap.set(tripName, { files: 0, thumb: null })
        const t = tripMap.get(tripName)!
        t.files++
        if (!t.thumb && [".jpg", ".jpeg", ".png"].includes(f.suffix)) t.thumb = f.path
      }
      const entries: TripEntry[] = []
      for (const [name, info] of tripMap) {
        entries.push({ name, path: `${tripsRoot}/${name}`, fileCount: info.files, thumbnail: info.thumb })
      }
      entries.sort((a, b) => b.name.localeCompare(a.name))
      setTrips(entries)
    } catch { /* ignore */ }
    finally { setLoadingTrips(false) }
  }, [tripsRoot])

  // Load trips on mount if root is set
  useEffect(() => { if (tripsRoot) loadTrips() }, [tripsRoot])

  const handleCreate = async () => {
    if (!sourceDir || !label || !startDate || !endDate) return
    setCreating(true); setCreateError(null); setCreateResult(null)
    try {
      const options: TripOptions = {
        source_dirs: [sourceDir],
        target_root: tripsRoot,
        label,
        start_date: startDate,
        end_date: endDate,
        use_hardlinks: useHardlinks,
      }
      const preview = await tripPreview(options)
      if (preview.planned_count > 0) {
        const result = await tripApply(options)
        setCreateResult(result)
        loadTrips()
      }
    } catch (e) { setCreateError(String(e)) }
    finally { setCreating(false) }
  }

  // ── Trip Detail View ──
  if (selectedTrip) {
    return <TripDetailView trip={selectedTrip} onBack={() => setSelectedTrip(null)} />
  }

  // ── Main Dashboard ──
  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Plane className="w-6 h-6 text-primary" />
          <div>
            <h1 className="text-xl font-bold">Trips</h1>
            <p className="text-sm text-muted-foreground">Your trip collections.</p>
          </div>
        </div>
        <Button onClick={() => setShowCreate(true)} size="sm">
          <Plus className="w-4 h-4 mr-1" /> New Trip
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Input value={tripsRoot} onChange={e => { setTripsRoot(e.target.value); localStorage.setItem("trips_root", e.target.value) }} placeholder="Trips root directory (e.g. C:\Trips)" className="text-xs w-64" />
        <Button onClick={loadTrips} variant="outline" size="sm" disabled={!tripsRoot || loadingTrips}>
          {loadingTrips ? <Loader2 className="w-4 h-4 animate-spin" /> : "Refresh"}
        </Button>
        {trips.length > 0 && <Badge variant="secondary" className="ml-auto">{trips.length} trips</Badge>}
      </div>

      {trips.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {trips.map(trip => (
            <Card key={trip.name} className="overflow-hidden cursor-pointer hover:border-primary/50 transition-colors" onClick={() => setSelectedTrip(trip)}>
              <div className="aspect-video bg-muted relative overflow-hidden">
                {trip.thumbnail ? (
                  <img src={convertFileSrc(trip.thumbnail)} alt="" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center"><ImageOff className="w-10 h-10 text-muted-foreground/30" /></div>
                )}
              </div>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{trip.name}</p>
                    <p className="text-xs text-muted-foreground">{trip.fileCount} files</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : !loadingTrips ? (
        <EmptyState title="No trips yet" description={tripsRoot ? "Click 'New Trip' to create your first trip collection." : "Set your trips root directory above, then click Refresh."} />
      ) : null}

      {/* Create Trip Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>New Trip</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <label className="text-xs font-medium">Source Directory</label>
              <Input value={sourceDir} onChange={e => setSourceDir(e.target.value)} placeholder="C:\Photos" className="text-xs" />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium">Trip Label</label>
              <Input value={label} onChange={e => setLabel(e.target.value)} placeholder="Italy_2025" className="text-xs" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-medium">Start (YYYY-MM-DD)</label>
                <Input value={startDate} onChange={e => setStartDate(e.target.value)} placeholder="2025-06-01" className="text-xs" />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium">End (YYYY-MM-DD)</label>
                <Input value={endDate} onChange={e => setEndDate(e.target.value)} placeholder="2025-06-15" className="text-xs" />
              </div>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <label className="flex items-center gap-1"><input type="radio" checked={useHardlinks} onChange={() => setUseHardlinks(true)} /> Hardlinks</label>
              <label className="flex items-center gap-1"><input type="radio" checked={!useHardlinks} onChange={() => setUseHardlinks(false)} /> Copy</label>
            </div>
            {createError && <p className="text-xs text-red-400">{createError}</p>}
            {createResult && (
              <Card className="border-green-500/30"><CardContent className="py-2 text-xs">
                <p className="text-green-400">Trip created! {createResult.linked_count} linked, {createResult.copied_count} copied</p>
              </CardContent></Card>
            )}
          </div>
          <div className="flex justify-end gap-2 mt-2">
            <Button variant="ghost" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button size="sm" onClick={handleCreate} disabled={creating || !sourceDir || !label || !startDate || !endDate}>
              {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Trip"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
