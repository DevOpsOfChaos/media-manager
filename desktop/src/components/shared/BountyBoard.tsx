import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Heart, ThumbsUp } from "lucide-react"

const BOUNTIES = [
  { id: "gpu-faces", title_en: "GPU Face Detection", title_de: "GPU-Gesichtserkennung", description_en: "10-100x faster face detection using CUDA/OpenVINO", description_de: "10-100x schnellere Gesichtserkennung mit CUDA/OpenVINO", votes: 42, status: "planned" },
  { id: "mobile-app", title_en: "Mobile Companion App", title_de: "Mobile Begleit-App", description_en: "Browse library on phone, organize on desktop", description_de: "Bibliothek am Handy durchsuchen, am Desktop organisieren", votes: 38, status: "planned" },
  { id: "ai-tags", title_en: "AI Auto-Tagging", title_de: "KI Auto-Tagging", description_en: "Automatic object/scene detection and tagging", description_de: "Automatische Objekt-/Szenenerkennung und Tagging", votes: 35, status: "planned" },
  { id: "cloud-sync", title_en: "Cloud Sync", title_de: "Cloud-Sync", description_en: "Sync catalog and settings across devices", description_de: "Katalog und Einstellungen geräteübergreifend synchronisieren", votes: 31, status: "planned" },
  { id: "web-ui", title_en: "Web Interface", title_de: "Web-Oberfläche", description_en: "Browser-accessible interface for remote access", description_de: "Browser-basierte Oberfläche für Fernzugriff", votes: 27, status: "planned" },
  { id: "plugin-system", title_en: "Plugin System", title_de: "Plugin-System", description_en: "Community extensions for custom features", description_de: "Community-Erweiterungen für eigene Features", votes: 24, status: "planned" },
  { id: "multi-user", title_en: "Multi-User Support", title_de: "Mehrbenutzer-Unterstützung", description_en: "Separate catalogs and settings per user", description_de: "Getrennte Kataloge und Einstellungen pro Benutzer", votes: 19, status: "planned" },
  { id: "raw-editor", title_en: "RAW Editor", title_de: "RAW-Editor", description_en: "Basic RAW development adjustments", description_de: "Grundlegende RAW-Entwicklungseinstellungen", votes: 15, status: "planned" },
]

export function BountyBoard() {
  const t = useT()
  const [votes, setVotes] = useState<Record<string, number>>(() => {
    try { return JSON.parse(localStorage.getItem("bounty_votes") || "{}") }
    catch { return {} }
  })

  const vote = (id: string) => {
    const next = { ...votes, [id]: (votes[id] || 0) + 1 }
    setVotes(next)
    localStorage.setItem("bounty_votes", JSON.stringify(next))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Heart className="h-4 w-4 text-red-500" fill="currentColor" />
          {t("Feature Bounty Board", "Feature-Wunschliste")}
        </CardTitle>
        <CardDescription>
          {t("Vote for features you want to see next. Popular features get priority!",
             "Stimme für Features ab, die du als nächstes sehen willst. Beliebte Features bekommen Priorität!")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {BOUNTIES.map(b => (
          <div key={b.id} className="flex items-center gap-2 p-2 border rounded hover:bg-muted/30 transition-colors">
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{t(b.title_en, b.title_de)}</p>
              <p className="text-[10px] text-muted-foreground truncate">{t(b.description_en, b.description_de)}</p>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              <span className="text-[10px] font-mono text-muted-foreground">{b.votes + (votes[b.id] || 0)}</span>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => vote(b.id)}>
                <ThumbsUp className="h-3 w-3" />
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
