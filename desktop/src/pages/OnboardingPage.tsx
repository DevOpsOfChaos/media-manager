import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useSettingsStore } from "@/stores/settings-store"
import { open } from "@tauri-apps/plugin-dialog"
import { FolderOpen, Image, ArrowRight, Check, ChevronRight, ChevronLeft, Globe, Heart } from "lucide-react"

type Lang = "en" | "de"

function t(en: string, de: string, lang: Lang): string {
  return lang === "de" ? de : en
}

export default function OnboardingPage() {
  const [step, setStep] = useState(0)
  const [lang, setLang] = useState<Lang>(() => (useSettingsStore.getState().settings.language as Lang) || "en")
  const [selectedFolder, setSelectedFolder] = useState("")
  const [folderError, setFolderError] = useState("")
  const navigate = useNavigate()
  const { updateSettings, save } = useSettingsStore()

  const browseFolder = async () => {
    setFolderError("")
    try {
      const dir = await open({ directory: true, multiple: false, title: t("Select your photos folder", "Wähle deinen Foto-Ordner", lang) })
      if (dir && typeof dir === "string") {
        setSelectedFolder(dir)
        localStorage.setItem("default_source_dir", dir)
      }
    } catch {
      setFolderError(t("Could not open folder picker", "Ordner-Auswahl konnte nicht geöffnet werden", lang))
    }
  }

  const handleFinish = async () => {
    updateSettings({ show_onboarding: false, language: lang })
    await save()
    navigate("/")
  }

  const handleSkip = async () => {
    updateSettings({ show_onboarding: false, language: lang })
    await save()
    navigate("/")
  }

  const STEPS = [
    {
      title: t("Welcome to Media Manager", "Willkommen bei Media Manager", lang),
      description: t(
        "Organize, rename, and clean up your photo and video library — safely and with full undo support.",
        "Organisiere, benenne und bereinige deine Foto- und Videobibliothek — sicher und mit voller Rückgängig-Unterstützung.",
        lang
      ),
      icon: Image,
    },
    {
      title: t("Choose Your Media Sources", "Wähle deine Medien-Quellen", lang),
      description: t(
        "Tell Media Manager where your photos and videos live. This folder will be used as the default source across all tools.",
        "Sage Media Manager, wo deine Fotos und Videos liegen. Dieser Ordner wird als Standard-Quelle in allen Werkzeugen verwendet.",
        lang
      ),
      icon: FolderOpen,
    },
    {
      title: t("Language", "Sprache", lang),
      description: t(
        "Choose your preferred language. You can change this later in Settings.",
        "Wähle deine bevorzugte Sprache. Du kannst dies später in den Einstellungen ändern.",
        lang
      ),
      icon: Globe,
    },
    {
      title: t("You're All Set!", "Du bist startklar!", lang),
      description: t(
        "Start exploring the tools. We recommend beginning with Organize to preview how your files would be sorted.",
        "Erkunde die Werkzeuge. Wir empfehlen, mit Organize zu beginnen, um eine Vorschau zu sehen, wie deine Dateien sortiert würden.",
        lang
      ),
      icon: Check,
    },
  ]

  const currentStep = STEPS[step]
  const Icon = currentStep.icon

  return (
    <div className="flex items-center justify-center min-h-[80vh] p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center pb-2">
          <div className="mx-auto mb-4 flex items-center justify-center w-16 h-16 rounded-full bg-primary/10">
            <Icon className="w-8 h-8 text-primary" />
          </div>
          <CardTitle className="text-xl">{currentStep.title}</CardTitle>
          <p className="text-sm text-muted-foreground mt-2">{currentStep.description}</p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Step indicators */}
          <div className="flex justify-center gap-2">
            {STEPS.map((_, i) => (
              <div key={i} className={`w-2.5 h-2.5 rounded-full transition-colors ${i === step ? "bg-primary" : i < step ? "bg-primary/40" : "bg-muted"}`} />
            ))}
          </div>

          {/* STEP 0: Welcome + Language picker */}
          {step === 0 && (
            <div className="space-y-4">
              <ul className="space-y-2">
                {[
                  t("Preview every action before it happens", "Vorschau jeder Aktion vor der Ausführung", lang),
                  t("Undo any operation from the history page", "Jede Operation über die Verlaufsseite rückgängig machen", lang),
                  t("Group associated files (RAW+JPEG, XMP sidecars)", "Verknüpfte Dateien gruppieren (RAW+JPEG, XMP-Sidecars)", lang),
                  t("Find and remove exact duplicates", "Exakte Duplikate finden und entfernen", lang),
                ].map((d, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                    <span className="text-muted-foreground">{d}</span>
                  </li>
                ))}
              </ul>
              <div className="flex items-center gap-2 p-3 rounded-lg bg-muted/30">
                <Globe className="w-4 h-4 text-muted-foreground" />
                <select
                  value={lang}
                  onChange={e => setLang(e.target.value as Lang)}
                  className="text-sm bg-transparent border-none outline-none cursor-pointer"
                >
                  <option value="en">English</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>
            </div>
          )}

          {/* STEP 1: Folder picker */}
          {step === 1 && (
            <div className="space-y-4">
              <Button variant="outline" size="sm" onClick={browseFolder} className="w-full justify-start gap-2">
                <FolderOpen className="w-4 h-4" />
                {selectedFolder
                  ? selectedFolder
                  : t("Click to choose folder...", "Klicke um Ordner zu wählen...", lang)}
              </Button>
              {selectedFolder && (
                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                  <p className="text-sm font-medium text-green-400 flex items-center gap-2">
                    <Check className="w-4 h-4" />
                    {t("Folder selected", "Ordner ausgewählt", lang)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 break-all">{selectedFolder}</p>
                </div>
              )}
              {folderError && <p className="text-xs text-red-400">{folderError}</p>}
              <ul className="space-y-2">
                {[
                  t("This folder will be the default source for all tools", "Dieser Ordner wird Standard-Quelle für alle Werkzeuge", lang),
                  t("You can always change it later on each page", "Du kannst ihn später auf jeder Seite ändern", lang),
                  t("Subfolders are included automatically", "Unterordner werden automatisch einbezogen", lang),
                ].map((d, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                    <span className="text-muted-foreground">{d}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* STEP 2: Language */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setLang("en")}
                  className={`p-4 rounded-lg border-2 text-center transition-colors ${lang === "en" ? "border-primary bg-primary/10" : "border-border hover:border-primary/30"}`}
                >
                  <p className="text-lg font-bold">🇬🇧 English</p>
                  <p className="text-xs text-muted-foreground mt-1">English</p>
                </button>
                <button
                  onClick={() => setLang("de")}
                  className={`p-4 rounded-lg border-2 text-center transition-colors ${lang === "de" ? "border-primary bg-primary/10" : "border-border hover:border-primary/30"}`}
                >
                  <p className="text-lg font-bold">🇩🇪 Deutsch</p>
                  <p className="text-xs text-muted-foreground mt-1">German</p>
                </button>
              </div>
              <p className="text-xs text-muted-foreground text-center">
                {t("Language can be changed anytime in Settings", "Die Sprache kann jederzeit in den Einstellungen geändert werden", lang)}
              </p>
            </div>
          )}

          {/* STEP 3: Completion + Donate */}
          {step === 3 && (
            <div className="space-y-4">
              <ul className="space-y-2">
                {[
                  t("Organize: sort files into year/month/day folders", "Organize: Dateien in Jahr/Monat/Tag-Ordner sortieren", lang),
                  t("Duplicates: find and remove byte-identical copies", "Duplicates: Byte-identische Kopien finden und entfernen", lang),
                  t("Rename: standardize file names with metadata patterns", "Rename: Dateinamen mit Metadaten-Mustern standardisieren", lang),
                  t("People: face detection and person catalog", "People: Gesichtserkennung und Personen-Katalog", lang),
                  t("Trips: create collections from date ranges", "Trips: Sammlungen aus Datumsbereichen erstellen", lang),
                ].map((d, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm">
                    <Check className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
                    <span className="text-muted-foreground">{d}</span>
                  </li>
                ))}
              </ul>
              
              {/* Donate button */}
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/10 text-center">
                <Heart className="w-5 h-5 text-red-400 mx-auto mb-2" />
                <p className="text-sm font-medium">
                  {t("Support this project", "Unterstütze dieses Projekt", lang)}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {t("Media Manager is free and open source. Donations help keep development active.", "Media Manager ist kostenlos und Open Source. Spenden helfen, die Entwicklung aktiv zu halten.", lang)}
                </p>
                <Button variant="outline" size="sm" className="mt-3" disabled>
                  <Heart className="w-4 h-4 mr-1" />
                  {t("Donate (coming soon)", "Spenden (demnächst)", lang)}
                </Button>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between pt-2">
            <Button variant="ghost" size="sm" onClick={handleSkip}>
              {t("Skip", "Überspringen", lang)}
            </Button>
            <div className="flex gap-2">
              {step > 0 && (
                <Button variant="outline" size="sm" onClick={() => setStep(step - 1)}>
                  <ChevronLeft className="w-4 h-4 mr-1" /> {t("Back", "Zurück", lang)}
                </Button>
              )}
              {step < STEPS.length - 1 ? (
                <Button size="sm" onClick={() => setStep(step + 1)}>
                  {t("Next", "Weiter", lang)} <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              ) : (
                <Button size="sm" onClick={handleFinish}>
                  {t("Start Exploring", "Los geht's", lang)} <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
