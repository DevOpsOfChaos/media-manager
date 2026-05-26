import { useState, useCallback, useEffect, useRef } from "react"
import { useT } from "@/lib/i18n"
import { PageHeader } from "@/components/layout/PageHeader"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Switch } from "@/components/ui/switch"
import { peopleCatalogList, peoplePersonRename, peoplePersonCreate, peoplePersonReassign, peoplePersonMerge, peopleScan, peopleScanStatus, peopleFaceIgnore, peopleFaceAge, type PersonEntry, type CatalogListResponse } from "@/lib/tauri-bridge"
import { useProgress } from "@/lib/progress-context"
import { convertFileSrc } from "@tauri-apps/api/core"
import { EmptyState } from "@/components/shared/EmptyState"
 import { Users, Pencil, UserPlus, ArrowLeft, X, Check, ImageOff, GitMerge, MoreHorizontal, EyeOff, Zap } from "lucide-react"
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu"
import { FaceReviewSwiper } from "@/components/shared/FaceReviewSwiper"



// ── Thumbnail component ──
function FaceThumb({ path, size = 96, alt }: { path: string; size?: number; alt?: string }) {
  const t = useT()
  const [loaded, setLoaded] = useState(false)
  const [errored, setErrored] = useState(false)
  if (errored) return <div className="flex items-center justify-center bg-muted rounded" style={{ width: size, height: size }}><ImageOff className="w-6 h-6 text-muted-foreground" /></div>
  return (
    <div className="relative rounded overflow-hidden" style={{ width: size, height: size }}>
      {!loaded && <div className="absolute inset-0 bg-muted animate-pulse" />}
      <img src={convertFileSrc(path) || ""} alt={alt || path.split(/[\\/]/).pop() || t("Face", "Gesicht")} className="w-full h-full object-cover" onLoad={() => setLoaded(true)} onError={() => setErrored(true)} />
    </div>
  )
}

// ── Main component ──
export default function PeoplePage() {
  const t = useT()
  const { startProgress, updateProgress, finishProgress } = useProgress()

function friendlyPeopleError(err: unknown): string {
  const msg = String(err)
  if (msg.includes("dependencies")) return t("Could not scan for faces. Face recognition dependencies may not be installed.", "Gesichtserkennungs-Abhängigkeiten sind möglicherweise nicht installiert.")
  if (msg.includes("Permission")) return t("Cannot access source directory. Check folder permissions.", "Kein Zugriff auf das Quellverzeichnis. Ordnerberechtigungen prüfen.")
  if (msg.includes("catalog") && msg.includes("not found")) return t("Catalog file not found. Create one with the button below.", "Katalogdatei nicht gefunden. Mit dem Button unten erstellen.")
  if (msg.includes("corrupted") || msg.includes("invalid")) return t("Catalog file appears to be corrupted.", "Katalogdatei scheint beschädigt zu sein.")
  if (msg.includes("not found") && msg.includes("person")) return t("Person not found in catalog. Refresh and try again.", "Person nicht im Katalog gefunden. Aktualisieren und erneut versuchen.")
  if (msg.includes("already exists")) return t("A person with that name already exists.", "Eine Person mit diesem Namen existiert bereits.")
  return String(err).split("\n")[0].slice(0, 200)
}
  const [catalogPath, setCatalogPath] = useState(() => localStorage.getItem("people_catalog_path") || "")
  const [enabled, setEnabled] = useState(() => localStorage.getItem("people_scan_enabled") === "true")
  const [catalog, setCatalog] = useState<CatalogListResponse | null>(null)
  const [_loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sourceDir, _setSourceDir] = useState(() => localStorage.getItem("people_scan_source") || "")
  const [_scanResult, setScanResult] = useState<any>(null)
  const [_lastScanTime, setLastScanTime] = useState<string | null>(null)
  const [_scanStatus, setScanStatus] = useState<any>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

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

  // Merge dialog
  const [mergeDialog, setMergeDialog] = useState<{ from: PersonEntry } | null>(null)

  // Face swipe review
  const [showFaceSwiper, setShowFaceSwiper] = useState(false)

  const unknownFaces = (() => {
    if (!catalog) return []
    const unknown = catalog.people.find(p => p.person_id === "unknown" || p.person_id.startsWith("unknown"))
    if (!unknown) return []
    return unknown.source_paths.map(imagePath => ({ imagePath, personId: unknown.person_id }))
  })()

  // Age estimation cache
  const [ageCache, setAgeCache] = useState<Record<string, { bracket: string; confidence: number }>>({})
  const fetchAge = useCallback(async (facePath: string) => {
    if (ageCache[facePath]) return
    try {
      const result = await peopleFaceAge({ image_path: facePath, face_box: [0, 0, 100, 100] })
      setAgeCache(prev => ({ ...prev, [facePath]: { bracket: result.age_bracket, confidence: result.confidence } }))
    } catch { /* ignore */ }
  }, [ageCache])

  // Ignored faces
  const [ignoredFaces, setIgnoredFaces] = useState<Set<string>>(new Set())
  const loadIgnoredFaces = useCallback(async () => {
    if (!catalogPath) return
    try {
      const catalogDir = catalogPath.substring(0, catalogPath.lastIndexOf("/") !== -1 ? catalogPath.lastIndexOf("/") : catalogPath.lastIndexOf("\\"))
      if (!catalogDir) return
      const result = await peopleFaceIgnore({ action: "list", face_id: "", catalog_dir: catalogDir })
      if (result.ignored_faces) setIgnoredFaces(new Set(result.ignored_faces))
    } catch { /* ignore */ }
  }, [catalogPath])
  useEffect(() => { loadIgnoredFaces() }, [loadIgnoredFaces])

  const loadCatalog = useCallback(async () => {
    if (!catalogPath) return
    void setLoading(true)
    try {
      const data = await peopleCatalogList({ catalog_path: catalogPath })
      setCatalog(data)
    } catch (e) { setError(friendlyPeopleError(e)) }
    finally { void setLoading(false) }
  }, [catalogPath])

  useEffect(() => { loadCatalog() }, [loadCatalog])

  useEffect(() => {
    if (selectedPerson?.source_paths[0]) {
      fetchAge(selectedPerson.source_paths[0])
    }
  }, [selectedPerson, fetchAge])

  const handleToggle = async (checked: boolean) => {
    setEnabled(checked)
    localStorage.setItem("people_scan_enabled", String(checked))
    if (!checked) {
      if (pollingRef.current) clearInterval(pollingRef.current)
      return
    }
    if (!sourceDir) {
      setError(t("Please set a source directory first", "Bitte zuerst ein Quellverzeichnis festlegen"))
      return
    }
    localStorage.setItem("people_scan_source", sourceDir)
    localStorage.setItem("people_scan_catalog", catalogPath)
    setLoading(true)
    setError(null)
    startProgress(t("Scanning for faces...", "Suche nach Gesichtern..."), 100)
    try {
      const result = await peopleScan({
        source_dirs: [sourceDir],
        catalog_path: catalogPath || undefined,
        incremental: true,
        tolerance: 0.6,
      })
      updateProgress(100)
      setScanResult(result)
      setLastScanTime(new Date().toLocaleTimeString())
      const status = await peopleScanStatus({ source_dirs: [sourceDir] })
      setScanStatus(status)
    } catch (e) { setError(friendlyPeopleError(e)) }
    finally { setTimeout(() => finishProgress(), 500); setLoading(false) }
  }

  const handleRename = async () => {
    if (!selectedPerson || !editName.trim()) return
    try {
      await peoplePersonRename({ catalog_path: catalogPath, person_id: selectedPerson.person_id, name: editName.trim() })
      setEditingName(false)
      loadCatalog()
    } catch (e) { setError(friendlyPeopleError(e)) }
  }

  const handleCreatePerson = async () => {
    if (!createName.trim()) return
    try {
      await peoplePersonCreate({ catalog_path: catalogPath, name: createName.trim() })
      setShowCreatePerson(false)
      setCreateName("")
      loadCatalog()
    } catch (e) { setError(friendlyPeopleError(e)) }
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
    } catch (e) { setError(friendlyPeopleError(e)) }
  }

  const handleIgnoreFace = async (facePath: string) => {
    if (!catalogPath) return
    const catalogDir = catalogPath.substring(0, Math.max(catalogPath.lastIndexOf("/"), catalogPath.lastIndexOf("\\")))
    if (!catalogDir) return
    const faceId = `${facePath}::0`
    try {
      await peopleFaceIgnore({ action: "add", face_id: faceId, catalog_dir: catalogDir })
      setIgnoredFaces(prev => { const next = new Set(prev); next.add(faceId); return next })
    } catch (e) { console.error(e) }
  }

  // ── Person Grid View ──
  if (!selectedPerson) {
    return (
      <>
        <PageHeader
          title={t("People", "Personen")}
          subtitle={t("Recognized people from your photo library.", "Erkannte Personen aus Ihrer Fotobibliothek.")}
        >
          <Input value={catalogPath} onChange={e => { setCatalogPath(e.target.value); localStorage.setItem("people_catalog_path", e.target.value) }} placeholder={t("catalog.json", "catalog.json")} className="text-xs w-48" />
          <Button onClick={loadCatalog} size="sm" variant="outline" disabled={!catalogPath}>{t("Refresh", "Aktualisieren")}</Button>
          {unknownFaces.length > 0 && (
            <Button size="sm" variant="secondary" onClick={() => setShowFaceSwiper(true)}>
              <Zap className="w-3.5 h-3.5 mr-1" /> {t("Quick Review", "Schnellprüfung")}
            </Button>
          )}
        </PageHeader>
        <main className="flex flex-1 gap-4 p-4">
          <div className="flex-1 max-w-4xl mx-auto space-y-6">



        <div className="flex items-center gap-2">
          <Switch checked={enabled} onCheckedChange={handleToggle} />
          <span className="text-sm text-muted-foreground">{t("Auto-scan", "Auto-Scan")}</span>
          {catalog && <Badge variant="secondary" className="ml-auto">{catalog.person_count} {t("people", "Personen")}</Badge>}
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        {catalog && catalog.people.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {catalog.people.map(person => (
              <Card
                key={person.person_id}
                className="cursor-pointer hover:border-primary/50 transition-colors overflow-hidden relative group"
                role="button"
                tabIndex={0}
                aria-label={person.name}
                onClick={() => setSelectedPerson(person)}
                onKeyDown={(e) => e.key === 'Enter' && setSelectedPerson(person)}
              >
                <div className="aspect-square bg-muted">
                  {person.source_paths[0] ? (
                    <FaceThumb path={person.source_paths[0]} size={200} alt={person.name} />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center"><Users className="w-10 h-10 text-muted-foreground/40" /></div>
                  )}
                </div>
                <CardContent className="p-3">
                  <p className="text-sm font-medium truncate">{person.name}</p>
                  <p className="text-xs text-muted-foreground">{person.face_count} {t("faces", "Gesichter")}</p>
                </CardContent>
                <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-7 w-7 rounded-full"><MoreHorizontal className="h-3.5 w-3.5" /></Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuItem onClick={() => setMergeDialog({ from: person })}>
                        <GitMerge className="h-3.5 w-3.5 mr-2" />
                        {t("Merge into...", "Zusammenführen mit...")}
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </Card>
            ))}
            <Card className="cursor-pointer hover:border-primary/50 border-dashed flex items-center justify-center min-h-[200px]" role="button" tabIndex={0} onClick={() => setShowCreatePerson(true)} onKeyDown={(e) => e.key === 'Enter' && setShowCreatePerson(true)}>
              <div className="text-center text-muted-foreground">
                <UserPlus className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">{t("Add Person", "Person hinzufügen")}</p>
              </div>
            </Card>
          </div>
        ) : catalog ? (
          <EmptyState title={t("No people yet", "Noch keine Personen")} description={t("Scan photos with a catalog to recognize people, or add them manually.", "Scannen Sie Fotos mit einem Katalog, um Personen zu erkennen, oder fügen Sie sie manuell hinzu.")} />
        ) : (
          <EmptyState title={t("No catalog loaded", "Kein Katalog geladen")} description={t("Enter a catalog path above and click Refresh to see recognized people.", "Geben Sie oben einen Katalogpfad ein und klicken Sie Aktualisieren, um erkannte Personen zu sehen.")} />
        )}

        <Dialog open={showCreatePerson} onOpenChange={setShowCreatePerson}>
          <DialogContent className="max-w-sm">
            <DialogHeader><DialogTitle>{t("Add Person", "Person hinzufügen")}</DialogTitle></DialogHeader>
            <div className="space-y-3">
              <Input value={createName} onChange={e => setCreateName(e.target.value)} placeholder={t("Person name", "Name der Person")} autoFocus onKeyDown={e => e.key === "Enter" && handleCreatePerson()} />
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="sm" onClick={() => setShowCreatePerson(false)}>{t("Cancel", "Abbrechen")}</Button>
                <Button size="sm" onClick={handleCreatePerson} disabled={!createName.trim()}>{t("Create", "Erstellen")}</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {showFaceSwiper && (
          <FaceReviewSwiper
            faces={unknownFaces}
            catalogPath={catalogPath}
            onClose={() => { setShowFaceSwiper(false); loadCatalog() }}
          />
        )}

        {mergeDialog && (
          <Dialog open onOpenChange={() => setMergeDialog(null)}>
            <DialogContent className="max-w-sm">
              <DialogHeader>
                <DialogTitle>{t("Merge Person", "Person zusammenführen")}</DialogTitle>
                <DialogDescription>
                  {t(`Merge "${mergeDialog.from.name}" into another person. All faces and aliases will be moved.`,
                     `"${mergeDialog.from.name}" mit einer anderen Person zusammenführen. Alle Gesichter und Aliasse werden übertragen.`)}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-1 max-h-60 overflow-y-auto">
                {catalog?.people.filter(p => p.person_id !== mergeDialog.from.person_id).map(p => (
                  <button key={p.person_id}
                    className="w-full text-left p-2 rounded hover:bg-muted transition-colors flex items-center gap-2"
                    onClick={async () => {
                      try {
                        await peoplePersonMerge({
                          catalog_path: catalogPath,
                          from_person_id: mergeDialog.from.person_id,
                          to_person_id: p.person_id,
                        })
                        setMergeDialog(null)
                        loadCatalog()
                      } catch (e) { console.error(e) }
                    }}>
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{p.name}</span>
                    <Badge variant="outline" className="text-[10px] ml-auto">{p.face_count}</Badge>
                  </button>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        )}
          </div>
        </main>
      </>
    )
  }

  // ── Person Detail View ──
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" onClick={() => setSelectedPerson(null)}><ArrowLeft className="w-4 h-4 mr-1" /> {t("Back", "Zurück")}</Button>
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
          <p className="text-sm text-muted-foreground">{selectedPerson.face_count} {t("faces recognized", "Gesichter erkannt")}
            {selectedPerson.source_paths.length > 0 && ageCache[selectedPerson.source_paths[0]]?.bracket && ageCache[selectedPerson.source_paths[0]]?.bracket !== "unknown" && (
              <> &middot; <Badge variant="outline" className="text-[10px] align-middle">{t("Est. age:", "Geschätztes Alter:")} {ageCache[selectedPerson.source_paths[0]].bracket}</Badge></>
            )}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
        {selectedPerson.source_paths.filter(path => !ignoredFaces.has(`${path}::0`)).map((path, i) => (
          <div
            key={i}
            className="cursor-pointer rounded overflow-hidden hover:ring-2 hover:ring-primary transition-all"
            role="button"
            tabIndex={0}
            onClick={() => { setModalImage(path); setModalPersonId(selectedPerson.person_id); fetchAge(path) }}
            onKeyDown={(e) => e.key === 'Enter' && (setModalImage(path), setModalPersonId(selectedPerson.person_id), fetchAge(path))}
          >
            <FaceThumb path={path} size={150} alt={selectedPerson.name} />
          </div>
        ))}
        {selectedPerson.source_paths.filter(path => ignoredFaces.has(`${path}::0`)).length > 0 && (
          <p className="col-span-full text-xs text-muted-foreground">{t("Hidden:", "Ausgeblendet:")} {selectedPerson.source_paths.filter(path => ignoredFaces.has(`${path}::0`)).length} {t("ignored faces", "ignorierte Gesichter")}</p>
        )}
        {selectedPerson.source_paths.length === 0 && (
          <div className="col-span-full py-12 text-center text-muted-foreground">
            <ImageOff className="w-10 h-10 mx-auto mb-2" />
            <p>{t("No images for this person yet. Run a face scan to find matches.", "Noch keine Bilder für diese Person. Führen Sie einen Gesichtsscan durch, um Übereinstimmungen zu finden.")}</p>
          </div>
        )}
      </div>

      <Dialog open={!!modalImage} onOpenChange={(o: boolean) => { if (!o) { setModalImage(null); setShowReassign(false) } }}>
        <DialogContent className="max-w-2xl">
          <DialogHeader><DialogTitle className="text-sm">{modalImage?.split(/[\\/]/).pop()}</DialogTitle></DialogHeader>
          {modalImage && (
            <div className="space-y-4">
              <img src={convertFileSrc(modalImage) || ""} alt={modalImage?.split(/[\\/]/).pop() || t("Person image", "Personenbild")} className="w-full max-h-[60vh] object-contain rounded" />
              {!showReassign ? (
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">{t("Person:", "Person:")} {selectedPerson?.name}</span>
                    {modalImage && ageCache[modalImage]?.bracket && ageCache[modalImage]?.bracket !== "unknown" && (
                      <Badge variant="outline" className="text-[10px]">{ageCache[modalImage].bracket}</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" onClick={() => modalImage && handleIgnoreFace(modalImage)} title={t("Ignore this face", "Dieses Gesicht ignorieren")}>
                      <EyeOff className="w-3.5 h-3.5 mr-1" />
                      {t("Ignore", "Ignorieren")}
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setShowReassign(true)}>
                      {t("Not this person?", "Nicht diese Person?")}
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 p-3 border rounded border-yellow-500/30 bg-yellow-500/5">
                  <p className="text-sm font-medium">{t("Reassign this face", "Dieses Gesicht neu zuweisen")}</p>
                  <select
                    value={reassignToId}
                    onChange={e => setReassignToId(e.target.value)}
                    className="w-full text-xs rounded border border-border bg-background px-2 py-1.5"
                  >
                    <option value="">{t("-- Create new person --", "-- Neue Person erstellen --")}</option>
                    {catalog?.people.filter(p => p.person_id !== selectedPerson?.person_id).map(p => (
                      <option key={p.person_id} value={p.person_id}>{p.name} ({p.face_count} {t("faces", "Gesichter")})</option>
                    ))}
                  </select>
                  {!reassignToId && (
                    <Input value={newPersonName} onChange={e => setNewPersonName(e.target.value)} placeholder={t("New person name", "Neuer Personenname")} className="text-xs" />
                  )}
                  <div className="flex justify-end gap-2">
                    <Button variant="ghost" size="sm" onClick={() => setShowReassign(false)}>{t("Cancel", "Abbrechen")}</Button>
                    <Button size="sm" onClick={handleReassign} disabled={!reassignToId && !newPersonName.trim()}>
                      {reassignToId ? t("Reassign", "Neu zuweisen") : t("Create & Reassign", "Erstellen & Zuweisen")}
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
