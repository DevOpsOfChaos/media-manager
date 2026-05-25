import { useState, useEffect, useCallback } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { EmptyState } from "@/components/shared/EmptyState"
import { peopleCatalogList, type PersonEntry } from "@/lib/tauri-bridge"
import { convertFileSrc } from "@tauri-apps/api/core"
import { User, Calendar, Loader2, ArrowLeft } from "lucide-react"

export default function FaceTimelinePage() {
  const t = useT()
  const [catalogPath, setCatalogPath] = useState(() => localStorage.getItem("default_catalog_path") || "")
  const [people, setPeople] = useState<PersonEntry[]>([])
  const [selectedPerson, setSelectedPerson] = useState<PersonEntry | null>(null)
  const [loading, setLoading] = useState(false)

  const loadCatalog = useCallback(async () => {
    if (!catalogPath) return
    setLoading(true)
    try {
      const result = await peopleCatalogList({ catalog_path: catalogPath })
      setPeople(result.people)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [catalogPath])

  useEffect(() => {
    if (catalogPath) loadCatalog()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center gap-3">
        <User className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-xl font-bold">{t("Face Timeline", "Gesichter-Zeitleiste")}</h1>
          <p className="text-sm text-muted-foreground">
            {t("Browse all photos of a person, sorted by date.", "Alle Fotos einer Person nach Datum sortiert durchsuchen.")}
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        <Input
          value={catalogPath}
          onChange={e => setCatalogPath(e.target.value)}
          placeholder={t("Catalog path", "Katalog-Pfad")}
          className="text-xs flex-1"
        />
        <Button size="sm" onClick={loadCatalog} disabled={loading}>
          {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : t("Load", "Laden")}
        </Button>
      </div>

      {people.length > 0 && !selectedPerson && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
          {people.map(p => (
            <Card
              key={p.person_id}
              className="cursor-pointer hover:border-primary/50 transition-colors"
              onClick={() => setSelectedPerson(p)}
              role="button"
              tabIndex={0}
              onKeyDown={e => e.key === "Enter" && setSelectedPerson(p)}
            >
              <CardContent className="p-3 text-center">
                <div className="w-12 h-12 rounded-full bg-muted mx-auto mb-2 flex items-center justify-center">
                  <User className="w-6 h-6 text-muted-foreground" />
                </div>
                <p className="text-sm font-medium truncate">{p.name}</p>
                <p className="text-[10px] text-muted-foreground">{p.face_count} {t("photos", "Fotos")}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {selectedPerson && (
        <>
          <Button variant="outline" size="sm" onClick={() => setSelectedPerson(null)}>
            <ArrowLeft className="h-3 w-3 mr-1" /> {t("Back to all people", "Zurück zu allen Personen")}
          </Button>
          <div className="space-y-3">
            {[...selectedPerson.source_paths].sort().reverse().map((path, i) => (
              <Card key={i} className="flex items-center gap-3 p-3">
                <img src={convertFileSrc(path)} className="h-16 w-16 rounded object-cover bg-muted" alt="" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate">{path.split("/").pop() || path.split("\\").pop()}</p>
                  <p className="text-[10px] text-muted-foreground truncate">{path}</p>
                </div>
                <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
              </Card>
            ))}
          </div>
        </>
      )}

      {!loading && people.length === 0 && (
        <EmptyState
          title={t("No catalog loaded", "Kein Katalog geladen")}
          description={t("Load a people catalog to browse face timelines.", "Lade einen Personenkatalog, um Zeitleisten zu durchsuchen.")}
        />
      )}
    </div>
  )
}
