import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Trash2, FolderSearch } from "lucide-react"

export interface SmartCollection {
  id: string
  name: string
  rules: {
    fileTypes?: string[]
    ratingMin?: number
    flagState?: "pick" | "reject"
    tags?: string[]
    dateFrom?: string
    dateTo?: string
    suffix?: string[]
  }
  createdAt: string
}

interface SmartCollectionsProps {
  onApply: (collection: SmartCollection) => void
}

export function SmartCollections({ onApply }: SmartCollectionsProps) {
  const t = useT()
  const [collections, setCollections] = useState<SmartCollection[]>(() => {
    try { return JSON.parse(localStorage.getItem("smart_collections") || "[]") }
    catch { return [] }
  })
  const [name, setName] = useState("")

  const create = () => {
    if (!name.trim()) return
    const collection: SmartCollection = {
      id: Date.now().toString(),
      name: name.trim(),
      rules: {},
      createdAt: new Date().toISOString(),
    }
    const next = [...collections, collection]
    setCollections(next)
    localStorage.setItem("smart_collections", JSON.stringify(next))
    setName("")
  }

  const remove = (id: string) => {
    const next = collections.filter(c => c.id !== id)
    setCollections(next)
    localStorage.setItem("smart_collections", JSON.stringify(next))
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder={t("New collection name...", "Neuer Sammlungsname...")}
          className="text-xs h-8"
          onKeyDown={e => e.key === "Enter" && create()}
        />
        <Button size="sm" onClick={create} disabled={!name.trim()} className="h-8">
          <Plus className="h-3 w-3 mr-1" /> {t("Create", "Erstellen")}
        </Button>
      </div>

      {collections.length > 0 ? (
        <div className="space-y-2">
          {collections.map(c => (
            <Card key={c.id} className="p-2 hover:bg-muted/30 transition-colors cursor-pointer"
              onClick={() => onApply(c)}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FolderSearch className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{c.name}</span>
                  <span className="text-[10px] text-muted-foreground">
                    {t("Saved filter", "Gespeicherter Filter")}
                  </span>
                </div>
                <Button variant="ghost" size="icon" className="h-6 w-6"
                  onClick={(e) => { e.stopPropagation(); remove(c.id) }}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <p className="text-xs text-muted-foreground text-center py-4">
          {t("No smart collections yet. Create one from current filters.", "Noch keine Smart Collections. Erstelle eine aus aktuellen Filtern.")}
        </p>
      )}
    </div>
  )
}
