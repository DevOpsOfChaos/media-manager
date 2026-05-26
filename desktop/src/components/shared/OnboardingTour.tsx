import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, X, FolderOpen, Image, Users, Scan, Settings, LayoutDashboard } from "lucide-react"

const STEPS = [
  {
    id: "welcome",
    icon: LayoutDashboard,
    titleEn: "Welcome to Media Manager",
    titleDe: "Willkommen bei Media Manager",
    descriptionEn: "Your local-first media workflow assistant. Organize, deduplicate, and manage your photo library with face recognition and smart workflows.",
    descriptionDe: "Dein lokaler Medien-Workflow-Assistent. Organisiere, dedupliziere und verwalte deine Fotosammlung mit Gesichtserkennung und intelligenten Workflows.",
    tips: [
      { en: "All data stays on your computer — no cloud uploads", de: "Alle Daten bleiben auf deinem Computer — kein Cloud-Upload" },
      { en: "Works with 160,000+ files on a standard laptop", de: "Funktioniert mit 160.000+ Dateien auf einem Standard-Laptop" },
    ],
  },
  {
    id: "library",
    icon: Image,
    titleEn: "Library — Browse Your Media",
    titleDe: "Bibliothek — Medien durchsuchen",
    descriptionEn: "Browse all your organized photos and videos. Filter by type, date, tags, or ratings. Double-click to open, right-click for actions.",
    descriptionDe: "Durchsuche alle organisierten Fotos und Videos. Filtere nach Typ, Datum, Tags oder Bewertung. Doppelklick zum Öffnen, Rechtsklick für Aktionen.",
    tips: [
      { en: "Use star ratings and color labels to organize", de: "Nutze Sterne-Bewertungen und Farb-Labels zum Organisieren" },
      { en: "Press P to pick, X to reject for fast culling", de: "Drücke P zum Auswählen, X zum Ablehnen für schnelles Culling" },
    ],
  },
  {
    id: "organize",
    icon: FolderOpen,
    titleEn: "Organize — Sort Your Files",
    titleDe: "Organisieren — Dateien sortieren",
    descriptionEn: "Automatically sort photos into dated folders. Choose a pattern like Year/Month/Day. Use Hardlinks for instant results without copying.",
    descriptionDe: "Sortiere Fotos automatisch in datierte Ordner. Wähle ein Muster wie Jahr/Monat/Tag. Nutze Hardlinks für sofortige Ergebnisse ohne Kopieren.",
    tips: [
      { en: "Always Preview first to check results before Applying", de: "Immer erst Vorschau zeigen, dann Ausführen" },
      { en: "Hardlinks = instant, zero extra disk space", de: "Hardlinks = sofort, null Extra-Speicherplatz" },
    ],
  },
  {
    id: "duplicates",
    icon: Scan,
    titleEn: "Duplicates — Free Up Space",
    titleDe: "Duplikate — Speicher freigeben",
    descriptionEn: "Find exact and similar duplicate photos. Review matches and delete unwanted copies to free up disk space.",
    descriptionDe: "Finde exakte und ähnliche doppelte Fotos. Prüfe Treffer und lösche unerwünschte Kopien, um Speicher freizugeben.",
    tips: [
      { en: "Exact scan finds byte-identical copies", de: "Exakter Scan findet Byte-identische Kopien" },
      { en: "Similar scan uses perceptual hashing", de: "Ähnlichkeitsscan nutzt perceptual Hashing" },
    ],
  },
  {
    id: "people",
    icon: Users,
    titleEn: "People — Face Recognition",
    titleDe: "Personen — Gesichtserkennung",
    descriptionEn: "Scan photos for faces and group them by person. Review and confirm matches. Build a catalog of people in your library.",
    descriptionDe: "Scanne Fotos nach Gesichtern und gruppiere sie nach Person. Prüfe und bestätige Treffer. Erstelle einen Katalog der Personen.",
    tips: [
      { en: "Use fast mode for first scan, deep verify for accuracy", de: "Schnellmodus für ersten Scan, Tiefenprüfung für Genauigkeit" },
      { en: "Review unknown faces with the Quick Review (Tinder-style)", de: "Unbekannte Gesichter mit Quick Review prüfen (Tinder-Style)" },
    ],
  },
  {
    id: "tips",
    icon: Settings,
    titleEn: "Pro Tips",
    titleDe: "Profi-Tipps",
    descriptionEn: "Get the most out of Media Manager with these power-user features.",
    descriptionDe: "Hol das Maximum aus Media Manager mit diesen Power-User-Features.",
    tips: [
      { en: "Press ? anywhere to see keyboard shortcuts", de: "Drücke ? überall für Tastaturkürzel" },
      { en: "Mini Mode shrinks the window during long operations", de: "Mini-Modus verkleinert das Fenster bei langen Operationen" },
      { en: "Smart Collections save your filter combinations", de: "Smart Collections speichern deine Filter-Kombinationen" },
      { en: "Save settings as Favorites for quick reuse", de: "Speichere Einstellungen als Favoriten zur Wiederverwendung" },
    ],
  },
]

export function OnboardingTour({ onClose }: { onClose: () => void }) {
  const t = useT()
  const [step, setStep] = useState(0)
  const [exiting, setExiting] = useState(false)

  const current = STEPS[step]
  const isLast = step === STEPS.length - 1
  const isFirst = step === 0

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" && !isLast) setStep(s => s + 1)
      if (e.key === "ArrowLeft" && !isFirst) setStep(s => s - 1)
      if (e.key === "Escape") { setExiting(true); setTimeout(onClose, 200) }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [isLast, isFirst, onClose])

  const finish = () => {
    setExiting(true)
    setTimeout(() => {
      localStorage.setItem("onboarding_complete", "true")
      onClose()
    }, 200)
  }

  return (
    <div className={`fixed inset-0 z-50 bg-background flex flex-col transition-opacity duration-200 ${exiting ? "opacity-0" : "opacity-100"}`}>
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-3">
          <span className="text-2xl">📦</span>
          <span className="font-semibold">Media Manager</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex gap-1.5">
            {STEPS.map((_, i) => (
              <div key={i} className={`h-1.5 rounded-full transition-all ${
                i === step ? "w-6 bg-primary" : i < step ? "w-1.5 bg-primary/50" : "w-1.5 bg-muted"
              }`} />
            ))}
          </div>
          <Button variant="ghost" size="icon" onClick={() => { setExiting(true); setTimeout(onClose, 200) }}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-lg w-full text-center space-y-6">
          <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto">
            <current.icon className="w-10 h-10 text-primary" />
          </div>

          <div>
            <h1 className="text-2xl font-bold">{t(current.titleEn, current.titleDe)}</h1>
            <p className="text-muted-foreground mt-2 text-sm max-w-md mx-auto">
              {t(current.descriptionEn, current.descriptionDe)}
            </p>
          </div>

          {current.tips && (
            <div className="space-y-2 text-left max-w-sm mx-auto">
              {current.tips.map((tip, i) => (
                <div key={i} className="flex gap-2 text-sm">
                  <span className="text-primary mt-0.5">•</span>
                  <span className="text-muted-foreground">{t(tip.en, tip.de)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between p-4 border-t">
        <Button variant="ghost" onClick={finish} className="text-xs">
          {t("Skip tour", "Tour überspringen")}
        </Button>
        
        <div className="flex gap-2">
          {!isFirst && (
            <Button variant="outline" size="sm" onClick={() => setStep(s => s - 1)}>
              <ChevronLeft className="h-4 w-4 mr-1" /> {t("Back", "Zurück")}
            </Button>
          )}
          {isLast ? (
            <Button size="sm" onClick={finish}>
              {t("Get Started", "Los geht's")} ✨
            </Button>
          ) : (
            <Button size="sm" onClick={() => setStep(s => s + 1)}>
              {t("Next", "Weiter")} <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
