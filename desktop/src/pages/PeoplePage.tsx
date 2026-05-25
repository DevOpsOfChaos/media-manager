import { useState, useCallback, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Switch } from "@/components/ui/switch"
import { peopleCatalogList, peoplePersonRename, peoplePersonCreate, peoplePersonReassign, type PersonEntry, type CatalogListResponse } from "@/lib/tauri-bridge"
import { convertFileSrc } from "@tauri-apps/api/core"
import { EmptyState } from "@/components/shared/EmptyState"
import { Users, Pencil, UserPlus, ArrowLeft, X, Check, ImageOff } from "lucide-react"

// ── Thumbnail component ──
function FaceThumb({ path, size = 96 }: { path: string; size?: number }) {
  const [loaded, setLoaded] = useState(false)
  const [errored, setErrored] = useState(false)
  if (errored) return <div className="flex items-center justify-center bg-muted rounded" style={{ width: size, height: size }}><ImageOff className="w-6 h-6 text-muted-foreground" /></div>
  return (
    <div className="relative rounded overflow-hidden" style={{ width: size, height: size }}>
      {!loaded && <div className="absolute inset-0 bg-muted animate-pulse" />}
      <img src={convertFileSrc(path)} alt="" className="w-full h-full object-cover" onLoad={() => setLoaded(true)} onError={() => setErrored(true)} />
    </div>
  )
}

// ── Main component ──
export default function PeoplePage() {
  const [catalogPath, setCatalogPath] = useState(() => localStorage.getItem("people_catalog_path") || "")
  const [enabled, setEnabled] = useState(() => localStorage.getItem("people_scan_enabled") === "true")
  const [catalog, setCatalog] = useState<CatalogListResponse | null>(null)
  const [_loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Detail view
  const [selectedPerson, setSelectedPerson] = useState<PersonEntry | null>(null)
  const [editingName, setEditingName] = useState(false)
  const [editName, setEditName] = useState("")

  // Image modal
  const [modalImage, setModalImage] = useState<string | null>(null)
  const [modalPersonId, setModalPersonId] = useState<string | null>(null)

  // Reassign dialog
  const [showReassign, setShowReassign] = useState(false)
  const [reassignToId, setReassignToId] = useState("")
  const [newPersonName, setNewPersonName] = useState("")

  // Create person dialog
  const [showCreatePerson, setShowCreatePerson] = useState(false)
  const [createName, setCreateName] = useState("")

  const loadCatalog = useCallback(async () => {
    if (!catalogPath) return
    void setLoading(true)
    try {
      const data = await peopleCatalogList({ catalog_path: catalogPath })
      setCatalog(data)
    } catch (e) { setError(String(e)) }
    finally { void setLoading(false) }
  }, [catalogPath])

  useEffect(() => { loadCatalog() }, [loadCatalog])

  const handleToggle = (checked: boolean) => {
    setEnabled(checked)
    localStorage.setItem("people_scan_enabled", String(checked))
  }

  const handleRename = async () => {
    if (!selectedPerson || !editName.trim()) return
    try {
      await peoplePersonRename({ catalog_path: catalogPath, person_id: selectedPerson.person_id, name: editName.trim() })
      setEditingName(false)
      loadCatalog()
    } catch (e) { setError(String(e)) }
  }

  const handleCreatePerson = async () => {
    if (!createName.trim()) return
    try {
      await peoplePersonCreate({ catalog_path: catalogPath, name: createName.trim() })
      setShowCreatePerson(false)
      setCreateName("")
      loadCatalog()
    } catch (e) { setError(String(e)) }
  }

  const handleReassign = async () => {
    if (!modalImage || !modalPersonId) return
    try {
      await peoplePersonReassign({
        catalog_path: catalogPath,
        source_path: modalImage,
        face_index: 0,
        from_person_id: modalPersonId,
        to_person_id: reassignToId || undefined,
        to_person_name: reassignToId ? undefined : newPersonName || undefined,
      })
      setShowReassign(false)
      setModalImage(null)
      setReassignToId("")
      setNewPersonName("")
      loadCatalog()
    } catch (e) { setError(String(e)) }
  }

  // ── Person Grid View ──
  if (!selectedPerson) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-primary" />
            <div>
              <h1 className="text-xl font-bold">People</h1>
              <p className="text-sm text-muted-foreground">Recognized people from your photo library.</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Input value={catalogPath} onChange={e => { setCatalogPath(e.target.value); localStorage.setItem("people_catalog_path", e.target.value) }} placeholder="catalog.json" className="text-xs w-48" />
            <Button onClick={loadCatalog} size="sm" variant="outline" disabled={!catalogPath}>Refresh</Button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Switch checked={enabled} onCheckedChange={handleToggle} />
          <span className="text-sm text-muted-foreground">Auto-scan</span>
          {catalog && <Badge variant="secondary" className="ml-auto">{catalog.person_count} people</Badge>}
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        {catalog && catalog.people.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {catalog.people.map(person => (
              <Card
                key={person.person_id}
                className="cursor-pointer hover:border-primary/50 transition-colors overflow-hidden"
                onClick={() => setSelectedPerson(person)}
              >
                <div className="aspect-square bg-muted">
                  {person.source_paths[0] ? (
                    <FaceThumb path={person.source_paths[0]} size={200} />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center"><Users className="w-10 h-10 text-muted-foreground/40" /></div>
                  )}
                </div>
                <CardContent className="p-3">
                  <p className="text-sm font-medium truncate">{person.name}</p>
                  <p className="text-xs text-muted-foreground">{person.face_count} faces</p>
                </CardContent>
              </Card>
            ))}
            {/* Add Person card */}
            <Card className="cursor-pointer hover:border-primary/50 border-dashed flex items-center justify-center min-h-[200px]" onClick={() => setShowCreatePerson(true)}>
              <div className="text-center text-muted-foreground">
                <UserPlus className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">Add Person</p>
              </div>
            </Card>
          </div>
        ) : catalog ? (
          <EmptyState title="No people yet" description="Scan photos with a catalog to recognize people, or add them manually." />
        ) : (
          <EmptyState title="No catalog loaded" description="Enter a catalog path above and click Refresh to see recognized people." />
        )}

        {/* Create Person Dialog */}
        <Dialog open={showCreatePerson} onOpenChange={setShowCreatePerson}>
          <DialogContent className="max-w-sm">
            <DialogHeader><DialogTitle>Add Person</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input value={createName} onChange={e => setCreateName(e.target.value)} placeholder="Person name" autoFocus onKeyDown={e => e.key === "Enter" && handleCreatePerson()} />
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="sm" onClick={() => setShowCreatePerson(false)}>Cancel</Button>
                <Button size="sm" onClick={handleCreatePerson} disabled={!createName.trim()}>Create</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    )
  }

  // ── Person Detail View ──
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => setSelectedPerson(null)}><ArrowLeft className="w-4 h-4 mr-1" /> Back</Button>
        <div className="flex-1">
          {editingName ? (
            <div className="flex items-center gap-2">
              <Input value={editName} onChange={e => setEditName(e.target.value)} className="text-lg font-bold h-9 w-64" autoFocus onKeyDown={e => { if (e.key === "Enter") handleRename(); if (e.key === "Escape") setEditingName(false) }} />
              <Button size="sm" variant="ghost" onClick={handleRename}><Check className="w-4 h-4" /></Button>
              <Button size="sm" variant="ghost" onClick={() => setEditingName(false)}><X className="w-4 h-4" /></Button>
            </div>
          ) : (
            <h1 className="text-xl font-bold flex items-center gap-2">
              {selectedPerson.name}
              <Button variant="ghost" size="sm" onClick={() => { setEditName(selectedPerson.name); setEditingName(true) }}><Pencil className="w-3.5 h-3.5" /></Button>
            </h1>
          )}
          <p className="text-sm text-muted-foreground">{selectedPerson.face_count} faces recognized</p>
        </div>
      </div>

      {/* Image Grid */}
      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
        {selectedPerson.source_paths.map((path, i) => (
          <div
            key={i}
            className="cursor-pointer rounded overflow-hidden hover:ring-2 hover:ring-primary transition-all"
            onClick={() => { setModalImage(path); setModalPersonId(selectedPerson.person_id) }}
          >
            <FaceThumb path={path} size={150} />
          </div>
        ))}
        {selectedPerson.source_paths.length === 0 && (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            <ImageOff className="w-10 h-10 mx-auto mb-2" />
            <p>No images for this person yet. Run a face scan to find matches.</p>
          </div>
        )}
      </div>

      {/* Image Modal */}
      <Dialog open={!!modalImage} onOpenChange={(o: boolean) => { if (!o) { setModalImage(null); setShowReassign(false) } }}>
        <DialogContent className="max-w-2xl">
          <DialogHeader><DialogTitle className="text-sm">{modalImage?.split(/[\\/]/).pop()}</DialogTitle></DialogHeader>
          {modalImage && (
            <div className="space-y-4">
              <img src={convertFileSrc(modalImage)} alt="" className="w-full max-h-[60vh] object-contain rounded" />
              {!showReassign ? (
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Person: {selectedPerson?.name}</span>
                  <Button variant="outline" size="sm" onClick={() => setShowReassign(true)}>
                    Not this person?
                  </Button>
                </div>
              ) : (
                <div className="space-y-3 p-3 border rounded border-yellow-500/30 bg-yellow-500/5">
                  <p className="text-sm font-medium">Reassign this face</p>
                  <select
                    value={reassignToId}
                    onChange={e => setReassignToId(e.target.value)}
                    className="w-full text-xs rounded border border-border bg-background px-2 py-1.5"
                  >
                    <option value="">-- Create new person --</option>
                    {catalog?.people.filter(p => p.person_id !== selectedPerson?.person_id).map(p => (
                      <option key={p.person_id} value={p.person_id}>{p.name} ({p.face_count} faces)</option>
                    ))}
                  </select>
                  {!reassignToId && (
                    <Input value={newPersonName} onChange={e => setNewPersonName(e.target.value)} placeholder="New person name" className="text-xs" />
                  )}
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="sm" onClick={() => setShowReassign(false)}>Cancel</Button>
                    <Button size="sm" onClick={handleReassign} disabled={!reassignToId && !newPersonName.trim()}>
                      {reassignToId ? "Reassign" : "Create & Reassign"}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
