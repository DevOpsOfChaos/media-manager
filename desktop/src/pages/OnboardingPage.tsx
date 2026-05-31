import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { PageHeader } from "@/components/layout/PageHeader"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useSettingsStore } from "@/stores/settings-store"
import { setAutostart } from "@/lib/tauri-bridge"
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
  const [onboardingAutoStart, setOnboardingAutoStart] = useState(false)
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
    if (onboardingAutoStart) {
      try { await setAutostart({ enable: true }) } catch {}
    }
    navigate("/")
  }

  const handleSkip = async () => {
    updateSettings({ show_onboarding: false, language: lang })
    await save()
    navigate("/")
  }

  const STEPS = [
    {
      title: t("Choose Your Language", "Wähle deine Sprache", lang),
      description: t(
        "This can be changed later in Settings.",
        "Kann später in den Einstellungen geändert werden.",
        lang
      ),
      icon: Globe,
    },
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
      title: t("How It Works", "So funktioniert's", lang),
      description: t(
        "Media Manager lets you preview every change before applying it. Nothing happens without your approval.",
        "Media Manager zeigt dir jede Änderung in der Vorschau, bevor sie angewendet wird. Nichts passiert ohne deine Zustimmung.",
        lang
      ),
      icon: FolderOpen,
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
    <>
      <PageHeader
        title={t("Setup Wizard", "Einrichtungs-Assistent", lang)}
        subtitle={t("Configure Media Manager to get started.", "Konfigurieren Sie Media Manager für den Einstieg.", lang)}
      />
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

          {/* STEP 0: Language selection FIRST */}
          {step === 0 && (
            <div className="space-y-4">
              <p className="text-muted-foreground text-center">
                {t("This can be changed later in Settings.", "Kann später in den Einstellungen geändert werden.", lang)}
              </p>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => { setLang("en"); updateSettings({ language: "en" }); setStep(step + 1) }}
                  className={`p-6 rounded-xl border-2 text-center transition-all ${
                    lang === "en" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}
                >
                  <span className="text-4xl mb-2 block">🇬🇧</span>
                  <span className="font-semibold">English</span>
                </button>
                <button
                  onClick={() => { setLang("de"); updateSettings({ language: "de" }); setStep(step + 1) }}
                  className={`p-6 rounded-xl border-2 text-center transition-all ${
                    lang === "de" ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
                  }`}
                >
                  <span className="text-4xl mb-2 block">🇩🇪</span>
                  <span className="font-semibold">Deutsch</span>
                </button>
              </div>
            </div>
          )}

          {/* STEP 1: Welcome + Folder picker */}
          {step === 1 && (
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
              <div className="border-t pt-4">
                <Button variant="outline" size="sm" onClick={browseFolder} className="w-full justify-start gap-2">
                  <FolderOpen className="w-4 h-4" />
                  {selectedFolder
                    ? selectedFolder
                    : t("Click to choose folder...", "Klicke um Ordner zu wählen...", lang)}
                </Button>
                {selectedFolder && (
                  <div className="mt-3 p-3 rounded-lg bg-green-500/10 dark:bg-green-500/15 border border-green-500/20 dark:border-green-400/20">
                    <p className="text-sm font-medium text-green-400 flex items-center gap-2">
                      <Check className="w-4 h-4" />
                      {t("Folder selected", "Ordner ausgewählt", lang)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1 break-all">{selectedFolder}</p>
                  </div>
                )}
                {folderError && <p className="text-xs text-red-400 mt-2">{folderError}</p>}
                <ul className="space-y-2 mt-3">
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
            </div>
          )}

          {/* STEP 2: Pattern / organize preferences */}
          {step === 2 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {t(
                  "Media Manager organizes files into a clean folder structure based on date and metadata patterns. You control the naming scheme per tool.",
                  "Media Manager organisiert Dateien in eine saubere Ordnerstruktur basierend auf Datum und Metadaten-Mustern. Du bestimmst das Namensschema pro Werkzeug.",
                  lang
                )}
              </p>
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-muted/30 border">
                  <p className="text-sm font-medium">{t("Default pattern", "Standard-Muster", lang)}</p>
                  <p className="text-xs text-muted-foreground font-mono mt-1">{t("{YYYY}/{MM}/{DD}_{stem}", "{YYYY}/{MM}/{DD}_{stem}", lang)}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {t("Creates year/month/day folders with original filenames.", "Erstellt Jahr/Monat/Tag-Ordner mit originalen Dateinamen.", lang)}
                  </p>
                </div>
                <p className="text-xs text-muted-foreground">
                  {t("Patterns can be customized later in the Organize page before any action is applied.", "Muster können später auf der Organize-Seite vor jeder Aktion angepasst werden.", lang)}
                </p>
              </div>
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

              {/* Auto-start option */}
              <label className="flex items-center justify-between p-3 border rounded cursor-pointer">
                <div>
                  <span className="font-medium">{t("Auto-start with Windows", "Mit Windows starten", lang)}</span>
                  <p className="text-xs text-muted-foreground">{t("Media Manager starts with your computer and checks for new images", "Media Manager startet mit deinem Computer und prüft auf neue Bilder", lang)}</p>
                </div>
                <Switch checked={onboardingAutoStart} onCheckedChange={setOnboardingAutoStart} />
              </label>
              
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
    </>
  )
}
