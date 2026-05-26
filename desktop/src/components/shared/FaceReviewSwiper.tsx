import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { convertFileSrc } from "@tauri-apps/api/core"
import { Check, X, SkipForward, User } from "lucide-react"

interface FaceReviewSwiperProps {
  faces: Array<{ imagePath: string; faceBox?: { x: number; y: number; w: number; h: number }; personId?: string }>
  catalogPath: string
  onClose: () => void
}

export function FaceReviewSwiper({ faces, catalogPath, onClose }: FaceReviewSwiperProps) {
  const t = useT()
  const [index, setIndex] = useState(0)
  const [personName, setPersonName] = useState("")
  const [people, setPeople] = useState<Array<{ person_id: string; name: string; face_count: number }>>([])
  const [saving, setSaving] = useState(false)
  const [stats, setStats] = useState({ reviewed: 0, confirmed: 0, skipped: 0, newPersons: 0 })
  const [exiting, setExiting] = useState(false)

  useEffect(() => {
    if (!catalogPath) return
    import("@/lib/tauri-bridge").then(({ peopleCatalogList }) => {
      peopleCatalogList({ catalog_path: catalogPath })
        .then(r => setPeople(r.people))
        .catch(() => {})
    })
  }, [catalogPath])

  const currentFace = faces[index]
  if (!currentFace || index >= faces.length) {
    return (
      <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-2xl text-white font-bold">
            {t("All faces reviewed!", "Alle Gesichter geprüft!")} 🎉
          </p>
          <div className="text-white/70 text-sm space-y-1">
            <p>{t(`Reviewed: ${stats.reviewed}`, `Geprüft: ${stats.reviewed}`)}</p>
            <p>{t(`Confirmed: ${stats.confirmed}`, `Bestätigt: ${stats.confirmed}`)}</p>
            <p>{t(`Skipped: ${stats.skipped}`, `Übersprungen: ${stats.skipped}`)}</p>
            <p>{t(`New persons: ${stats.newPersons}`, `Neue Personen: ${stats.newPersons}`)}</p>
          </div>
          <Button onClick={onClose}>{t("Done", "Fertig")}</Button>
        </div>
      </div>
    )
  }

  const next = () => {
    if (saving) return
    setIndex(i => i + 1)
    setPersonName("")
    setSaving(false)
  }

  const confirmAsPerson = async (personId: string) => {
    setSaving(true)
    try {
      const { peoplePersonReassign } = await import("@/lib/tauri-bridge")
      await peoplePersonReassign({
        catalog_path: catalogPath,
        source_path: currentFace.imagePath,
        face_index: 0,
        from_person_id: currentFace.personId || "unknown",
        to_person_id: personId,
      })
      setStats(s => ({ ...s, reviewed: s.reviewed + 1, confirmed: s.confirmed + 1 }))
    } catch (e) { console.error(e) }
    next()
  }

  const confirmAsNewPerson = async () => {
    if (!personName.trim()) return
    setSaving(true)
    try {
      const { peoplePersonCreate } = await import("@/lib/tauri-bridge")
      const result = await peoplePersonCreate({ catalog_path: catalogPath, name: personName.trim() })
      const { peoplePersonReassign } = await import("@/lib/tauri-bridge")
      await peoplePersonReassign({
        catalog_path: catalogPath,
        source_path: currentFace.imagePath,
        face_index: 0,
        from_person_id: currentFace.personId || "unknown",
        to_person_id: result.person_id,
      })
      setStats(s => ({ ...s, reviewed: s.reviewed + 1, confirmed: s.confirmed + 1, newPersons: s.newPersons + 1 }))
    } catch (e) { console.error(e) }
    next()
  }

  const skipFace = () => {
    setStats(s => ({ ...s, reviewed: s.reviewed + 1, skipped: s.skipped + 1 }))
    next()
  }

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === "y") skipFace()
      if (e.key === "ArrowLeft") setIndex(i => Math.max(0, i - 1))
      if (e.key === "Escape" && !exiting) { setExiting(true); setTimeout(onClose, 300) }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [index, saving])

  return (
    <div className="fixed inset-0 z-50 bg-black/95 flex flex-col">
      <div className="h-1 bg-white/20">
        <div className="h-full bg-primary transition-all" style={{ width: `${(index / faces.length) * 100}%` }} />
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <img
          src={convertFileSrc(currentFace.imagePath) || ""}
          className="max-w-lg max-h-[70vh] object-contain rounded-lg shadow-2xl"
          alt={t("Face to review", "Zu prüfendes Gesicht")}
        />
      </div>

      <div className="p-4 bg-black/60 space-y-3">
        <div className="flex gap-2 overflow-x-auto pb-1">
          {people.slice(0, 8).map(p => (
            <Button key={p.person_id} variant="outline" size="sm"
              className="text-xs shrink-0 border-white/20 text-white hover:bg-white/10"
              onClick={() => confirmAsPerson(p.person_id)}
              disabled={saving}>
              <User className="h-3 w-3 mr-1" /> {p.name}
            </Button>
          ))}
        </div>

        <div className="flex gap-2">
          <Input
            value={personName}
            onChange={e => setPersonName(e.target.value)}
            placeholder={t("New person name...", "Neuer Personenname...")}
            className="text-sm bg-white/10 border-white/20 text-white placeholder:text-white/40"
            onKeyDown={e => e.key === "Enter" && confirmAsNewPerson()}
          />
          <Button onClick={confirmAsNewPerson} disabled={saving || !personName.trim()}
            className="bg-green-600 hover:bg-green-700">
            <Check className="h-4 w-4 mr-1" /> {t("Create", "Erstellen")}
          </Button>
        </div>

        <div className="flex items-center justify-center gap-4">
          <Button variant="ghost" size="sm" onClick={skipFace}
            className="text-white/70 hover:text-white">
            <SkipForward className="h-4 w-4 mr-1" /> {t("Skip", "Überspringen")} (→)
          </Button>
          <span className="text-white/50 text-sm">{index + 1} / {faces.length}</span>
          <Button variant="ghost" size="sm" onClick={onClose}
            className="text-white/70 hover:text-white">
            <X className="h-4 w-4 mr-1" /> {t("Close", "Schließen")}
          </Button>
        </div>
      </div>
    </div>
  )
}
