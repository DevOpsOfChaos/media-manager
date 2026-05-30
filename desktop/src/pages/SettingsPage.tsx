import { useCallback, useEffect, useState } from "react"
import { invoke } from "@tauri-apps/api/core"
import { useT } from "@/lib/i18n"
import { trackError } from "@/lib/error-tracker"
import { toast } from "@/lib/toast"
import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { useSettingsStore } from "@/stores/settings-store"
import {
  runtimeDiagnostics,
  type RuntimeDiagnostics,
} from "@/lib/tauri-bridge"
import type { Language, Theme, Density } from "@/types"
import { FolderSearch, X, Check, RotateCcw } from "lucide-react"


export default function SettingsPage() {
  const t = useT()
  const {
    settings,
    loading,
    error,
    dirty,
    saved,
    updateSettings,
    load,
    save,
    reset,
  } = useSettingsStore()

  const [diag, setDiag] = useState<RuntimeDiagnostics | null>(null)
  const [diagLoading, setDiagLoading] = useState(false)
  const [diagError, setDiagError] = useState<string | null>(null)
  const [diagOpen, setDiagOpen] = useState(false)
  const [discoveredFolders, setDiscoveredFolders] = useState<string[]>([])
  const [scanningFolders, setScanningFolders] = useState(false)
  const [defaultSourceDir, setDefaultSourceDir] = useState(
    () => localStorage.getItem("default_source_dir") || ""
  )
  const [showQuickSetup, setShowQuickSetup] = useState(() => !localStorage.getItem("quick_setup_done"))
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [justSaved, setJustSaved] = useState(false)

  useEffect(() => {
    load()
  }, [load])

  const validate = (key: string, value: string) => {
    if (key === "face_recognition_tolerance") {
      const num = Number(value)
      if (isNaN(num) || num < 0.1 || num > 1.0) {
        setErrors(prev => ({ ...prev, face_recognition_tolerance: t("Must be between 0.1 and 1.0", "Muss zwischen 0.1 und 1.0 liegen") }))
      } else {
        setErrors(prev => {
          const next = { ...prev }
          delete next.face_recognition_tolerance
          return next
        })
      }
    }
  }

  const handleSave = useCallback(async () => {
    await save()
    setJustSaved(true)
    toast("success", t("Settings saved", "Einstellungen gespeichert"))
    setTimeout(() => setJustSaved(false), 2000)
  }, [save, t])

  const handleReset = useCallback(() => {
    if (confirm(t("Reset all settings to defaults?", "Alle Einstellungen zurücksetzen?"))) {
      reset()
      toast("info", t("Settings reset", "Einstellungen zurückgesetzt"))
    }
  }, [reset, t])

  const runDiag = useCallback(async () => {
    setDiagLoading(true)
    setDiagError(null)
    try {
      const result = await runtimeDiagnostics()
      setDiag(result)
    } catch (err) {
      trackError("settings.diagnostics", err)
      setDiagError(String(err))
    } finally {
      setDiagLoading(false)
    }
  }, [])

  const pythonOk = diag?.python_reachable === true

  const handleScanMediaFolders = useCallback(async () => {
    setScanningFolders(true)
    setDiscoveredFolders([])
    try {
      const home = await invoke<string>("get_home_dir").catch(() => {
        const env = typeof process !== "undefined" ? (process.env.HOME || process.env.USERPROFILE || "C:\\Users") : "C:\\Users"
        return env
      })
      const isWin = home.includes("\\")
      const candidates: string[] = isWin
        ? [home, `${home}\\Pictures`, `${home}\\Desktop`, `${home}\\Downloads`, `${home}\\Documents`, `${home}\\Videos`]
        : [`${home}/Pictures`, `${home}/Desktop`, `${home}/Downloads`, `${home}/Documents`, `${home}/Videos`]

      const existing: string[] = []
      for (const c of [...new Set(candidates)]) {
        try {
          const exists = await invoke<boolean>("path_exists", { path: c }).catch(() => false)
          if (exists) existing.push(c)
        } catch {
          // skip
        }
      }
      setDiscoveredFolders(existing)
    } catch {
      const home = typeof process !== "undefined" ? (process.env.HOME || process.env.USERPROFILE || "C:\\Users") : "C:\\Users"
      const isWin = home.includes("\\")
      setDiscoveredFolders(isWin
        ? ["C:\\Users\\Public\\Pictures", `${home}\\Pictures`, `${home}\\Desktop`, `${home}\\Downloads`]
        : [`${home}/Pictures`, `${home}/Desktop`, `${home}/Downloads`])
    } finally {
      setScanningFolders(false)
    }
  }, [])

  const handleSetDefaultSource = (folder: string) => {
    setDefaultSourceDir(folder)
    localStorage.setItem("default_source_dir", folder)
  }

  const hasErrors = Object.keys(errors).length > 0

  return (
    <>
      <PageHeader title={t("Settings", "Einstellungen")} />
      <main className="flex flex-1 gap-4 p-6">
        <div className="flex-1 max-w-5xl space-y-4">

          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              {error}
            </div>
          )}
          {saved && (
            <div className="rounded-lg border border-green-500/50 bg-green-500/10 px-4 py-3 text-sm text-green-600 dark:text-green-400">
              {t("Settings saved successfully.", "Einstellungen erfolgreich gespeichert.")}
            </div>
          )}

          <div className="flex items-center gap-3">
            <Button variant="default" size="sm" onClick={handleSave} disabled={loading || hasErrors}>
              {justSaved ? <Check className="h-4 w-4 mr-1" /> : null}
              {justSaved ? t("Saved!", "Gespeichert!") : loading ? t("Saving...", "Speichere...") : t("Save Settings", "Einstellungen speichern")}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleReset} disabled={loading}>
              <RotateCcw className="h-3 w-3 mr-1" /> {t("Reset to defaults", "Auf Standard zurücksetzen")}
            </Button>
            {dirty && (
              <span className="text-xs text-muted-foreground">
                {t("Unsaved changes", "Ungespeicherte Änderungen")}
              </span>
            )}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>{t("General", "Allgemein")}</CardTitle>
              <CardDescription>
                {t("Language, theme, density, and startup preferences.", "Sprache, Design, Dichte und Starteinstellungen.")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Language", "Sprache")}</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.language}
                  onChange={(e) =>
                    updateSettings({ language: e.target.value as Language })
                  }
                >
                  <option value="en">English</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Theme", "Design")}</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.theme}
                  onChange={(e) =>
                    updateSettings({ theme: e.target.value as Theme })
                  }
                >
                  <option value="modern-dark">{t("Dark", "Dunkel")}</option>
                  <option value="modern-light">{t("Light", "Hell")}</option>
                  <option value="system">{t("System", "System")}</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Density", "Dichte")}</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.density}
                  onChange={(e) =>
                    updateSettings({ density: e.target.value as Density })
                  }
                >
                  <option value="comfortable">{t("Comfortable", "Komfortabel")}</option>
                  <option value="compact">{t("Compact", "Kompakt")}</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Start Page", "Startseite")}</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.start_page_id}
                  onChange={(e) =>
                    updateSettings({ start_page_id: e.target.value })
                  }
                >
                  <option value="dashboard">{t("Dashboard", "Dashboard")}</option>
                  <option value="library">{t("Library", "Bibliothek")}</option>
                  <option value="organize">{t("Organize", "Organisieren")}</option>
                  <option value="duplicates">{t("Duplicates", "Duplikate")}</option>
                  <option value="people">{t("People", "Personen")}</option>
                  <option value="history">{t("History", "Verlauf")}</option>
                </select>
              </div>

              <Separator />

              <p className="text-xs font-medium text-muted-foreground">{t("Behavior", "Verhalten")}</p>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-input"
                  checked={settings.confirm_before_apply}
                  onChange={(e) =>
                    updateSettings({ confirm_before_apply: e.target.checked })
                  }
                />
                <span className="text-sm">
                  {t("Confirm before applying changes to files", "Vor dem Anwenden von Änderungen an Dateien bestätigen")}
                </span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-input"
                  checked={settings.enable_command_palette}
                  onChange={(e) =>
                    updateSettings({ enable_command_palette: e.target.checked })
                  }
                />
                <span className="text-sm">{t("Enable command palette (Ctrl+K)", "Befehlspalette aktivieren (Strg+K)")}</span>
              </label>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-input"
                  checked={settings.show_onboarding}
                  onChange={(e) =>
                    updateSettings({ show_onboarding: e.target.checked })
                  }
                />
                <span className="text-sm">{t("Show onboarding for new users", "Onboarding für neue Benutzer anzeigen")}</span>
              </label>

              <Button variant="outline" size="sm" onClick={() => {
                localStorage.removeItem("onboarding_complete")
                window.location.reload()
              }}>
                {t("Restart onboarding tour", "Onboarding-Tour neu starten")}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("Library", "Bibliothek")}</CardTitle>
              <CardDescription>
                {t("Default source directory, media folder discovery, and cache settings.", "Standard-Quellverzeichnis, Erkennung von Medienordnern und Cache-Einstellungen.")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {showQuickSetup && (
                <div className="rounded-lg border border-blue-200 dark:border-blue-800/40 bg-blue-50/30 dark:bg-blue-950/30 p-3 mb-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-sm">{t("Quick Setup", "Schnell einrichten")}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {t("Set your default source directory and language to get started quickly.", "Lege dein Standard-Quellverzeichnis und die Sprache fest für einen schnellen Start.")}
                      </p>
                    </div>
                    <Button variant="ghost" size="icon" className="h-6 w-6 shrink-0" onClick={() => { setShowQuickSetup(false); localStorage.setItem("quick_setup_done", "true") }}>
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Default source directory", "Standard-Quellverzeichnis")}</label>
                <Input
                  type="text"
                  placeholder={t("e.g. C:\\Photos", "z.B. C:\\Fotos")}
                  value={defaultSourceDir}
                  onChange={(e) => { setDefaultSourceDir(e.target.value); localStorage.setItem("default_source_dir", e.target.value) }}
                />
              </div>

              <Button variant="outline" size="sm" onClick={handleScanMediaFolders} disabled={scanningFolders}>
                <FolderSearch className="h-4 w-4 mr-2" />
                {scanningFolders ? t("Scanning...", "Suche...") : t("Scan for media folders", "Nach Medienordnern suchen")}
              </Button>

              {discoveredFolders.length > 0 && (
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">{t("Discovered folders:", "Gefundene Ordner:")}</p>
                  <div className="flex flex-wrap gap-2">
                    {discoveredFolders.map((folder) => (
                      <Badge
                        key={folder}
                        variant={folder === defaultSourceDir ? "default" : "secondary"}
                        className="cursor-pointer hover:opacity-80"
                        role="button"
                        tabIndex={0}
                        onClick={() => handleSetDefaultSource(folder)}
                        onKeyDown={(e) => e.key === "Enter" && handleSetDefaultSource(folder)}
                      >
                        {folder}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <Separator />

              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Cache", "Cache")}</label>
                <p className="text-xs text-muted-foreground">
                  {t("Clear cached thumbnails and temporary files to free up disk space.", "Zwischengespeicherte Miniaturansichten und temporäre Dateien löschen, um Speicherplatz freizugeben.")}
                </p>
                <Button variant="outline" size="sm" onClick={async () => {
                  try {
                    await invoke("clear_cache").catch(() => {})
                    toast("success", t("Cache cleared", "Cache geleert"))
                  } catch {
                    toast("error", t("Failed to clear cache", "Cache konnte nicht geleert werden"))
                  }
                }}>
                  {t("Clear cache", "Cache leeren")}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("Face Recognition", "Gesichtserkennung")}</CardTitle>
              <CardDescription>
                {t("Configure face recognition tolerance, backend, and GPU acceleration.", "Toleranz, Backend und GPU-Beschleunigung für die Gesichtserkennung konfigurieren.")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Tolerance", "Toleranz")}</label>
                <Input
                  type="number"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={settings.face_recognition_tolerance}
                  onChange={(e) => {
                    const val = e.target.value
                    validate("face_recognition_tolerance", val)
                    updateSettings({ face_recognition_tolerance: Number(val) })
                  }}
                  className={errors.face_recognition_tolerance ? "border-destructive" : ""}
                />
                {errors.face_recognition_tolerance && (
                  <p className="text-xs text-destructive">{errors.face_recognition_tolerance}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  {t("Lower values = stricter matching (0.1), higher values = more matches (1.0).", "Niedrigere Werte = strengerer Abgleich (0.1), höhere Werte = mehr Treffer (1.0).")}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">{t("Backend", "Backend")}</label>
                <select
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                  value={settings.face_recognition_backend}
                  onChange={(e) =>
                    updateSettings({ face_recognition_backend: e.target.value })
                  }
                >
                  <option value="opencv">OpenCV</option>
                  <option value="dlib">dlib</option>
                  <option value="insightface">InsightFace</option>
                </select>
              </div>

              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  className="h-4 w-4 rounded border-input"
                  checked={settings.face_recognition_gpu}
                  onChange={(e) =>
                    updateSettings({ face_recognition_gpu: e.target.checked })
                  }
                />
                <span className="text-sm">{t("Enable GPU acceleration (requires CUDA)", "GPU-Beschleunigung aktivieren (benötigt CUDA)")}</span>
              </label>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setDiagOpen(!diagOpen)}
                  className="text-left"
                  aria-expanded={diagOpen}
                >
                  <CardTitle>{t("Diagnostics", "Diagnose")}</CardTitle>
                  <CardDescription>
                    {t("Python bridge health and environment information.", "Python-Bridge-Status und Umgebungsinformationen.")}
                  </CardDescription>
                </button>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setDiagOpen(true)
                      runDiag()
                    }}
                    disabled={diagLoading}
                  >
                    {diagLoading ? (
                      <span className="inline-flex items-center gap-1">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                        {t("Checking...", "Prüfe...")}
                      </span>
                    ) : t("Refresh", "Aktualisieren")}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setDiagOpen(!diagOpen)}
                  >
                    {diagOpen ? t("Hide", "Verbergen") : t("Show", "Anzeigen")}
                  </Button>
                </div>
              </div>
            </CardHeader>
            {diagOpen && (
              <CardContent>
                {diagError && (
                  <div className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-xs text-destructive mb-3">
                    {diagError}
                  </div>
                )}

                {diag ? (
                  <div className="space-y-3 text-sm">
                    <StatusRow
                      label={t("Python Reachable", "Python erreichbar")}
                      ok={pythonOk}
                      detail={diag.python_error}
                    />
                    <StatusRow
                      label={t("media_manager import", "media_manager Import")}
                      ok={diag.media_manager_import?.ok}
                      detail={diag.media_manager_import?.error}
                    />
                    <StatusRow
                      label={t("bridge_settings import", "bridge_settings Import")}
                      ok={diag.bridge_settings_import?.ok}
                      detail={diag.bridge_settings_import?.error}
                    />
                    <StatusRow
                      label={t("Settings file", "Einstellungsdatei")}
                      ok={diag.settings_file_exists}
                      detail={
                        diag.settings_file_exists
                          ? diag.settings_path
                          : `${t("Not found:", "Nicht gefunden:")} ${diag.settings_path}`
                      }
                    />

                    <Separator />

                    <InfoRow label={t("Python executable", "Python-Programm")} value={diag.python_exe} />
                    <InfoRow
                      label={t("Python version", "Python-Version")}
                      value={diag.python_version ?? "\u2014"}
                    />
                    <InfoRow label={t("Project root", "Projektstamm")} value={diag.project_root} />
                    <InfoRow
                      label={t("PYTHONPATH", "PYTHONPATH")}
                      value={diag.pythonpath_prepended || "\u2014"}
                    />
                    {diag.settings_path_override && (
                      <InfoRow
                        label={t("Settings path override", "Einstellungspfad-Override")}
                        value={diag.settings_path_override}
                      />
                    )}

                    <Separator />

                    <p className="text-xs font-medium text-muted-foreground">
                      {t("Environment Hints", "Umgebungshinweise")}
                    </p>
                    <div className="grid grid-cols-2 gap-1 text-xs text-muted-foreground">
                      <EnvHint
                        label="MEDIA_MANAGER_PYTHON"
                        value={diag.env_hints.MEDIA_MANAGER_PYTHON}
                      />
                      <EnvHint
                        label="VIRTUAL_ENV"
                        value={diag.env_hints.VIRTUAL_ENV}
                      />
                      <EnvHint
                        label="CONDA_PREFIX"
                        value={diag.env_hints.CONDA_PREFIX}
                      />
                      <EnvHint
                        label="PROJECT_ROOT"
                        value={diag.env_hints.MEDIA_MANAGER_PROJECT_ROOT}
                      />
                    </div>

                    <Separator />

                    <p className="text-xs font-medium text-muted-foreground">
                      {t("System", "System")}
                    </p>
                    <InfoRow label={t("Python version", "Python-Version")} value={diag.python_version ?? "\u2014"} />
                    <InfoRow label={t("ExifTool version", "ExifTool-Version")} value={diag.exiftool_version ?? "\u2014"} />
                    <InfoRow label={t("CPU count", "CPU-Anzahl")} value={diag.system?.cpu_count != null ? String(diag.system.cpu_count) : "\u2014"} />
                    {diag.system?.disk_free_gb != null && (
                      <InfoRow
                        label={t("Disk free", "Speicher frei")}
                        value={`${diag.system.disk_free_gb} GB / ${diag.system.disk_total_gb} GB`}
                      />
                    )}
                    <StatusRow
                      label={t("OpenCV", "OpenCV")}
                      ok={diag.gpu?.opencv_dnn}
                      detail={diag.gpu?.opencv_version ?? undefined}
                    />
                    <StatusRow
                      label={t("CUDA", "CUDA")}
                      ok={diag.gpu?.cuda}
                      detail={diag.gpu?.recommendation ?? undefined}
                    />
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    {t("Click Refresh to check Python bridge health.", "Klicken Sie Aktualisieren, um die Python-Bridge zu prüfen.")}
                  </p>
                )}
              </CardContent>
            )}
          </Card>
        </div>
      </main>
    </>
  )
}

function StatusRow({
  label,
  ok,
  detail,
}: {
  label: string
  ok?: boolean
  detail?: string
}) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex size-2 shrink-0 rounded-full ${
          ok ? "bg-green-500 dark:bg-green-600" : "bg-destructive"
        }`}
      />
      <span className="font-medium">{label}</span>
      {detail && (
        <span className="truncate text-xs text-muted-foreground">
          {detail}
        </span>
      )}
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="truncate font-mono text-xs">{value}</span>
    </div>
  )
}

function EnvHint({
  label,
  value,
}: {
  label: string
  value: string | null | undefined
}) {
  const t = useT()
  return (
    <div className="flex items-center gap-1.5">
      <span
        className={`inline-flex size-1.5 rounded-full ${
          value ? "bg-green-500 dark:bg-green-600" : "bg-muted-foreground/30"
        }`}
      />
      <span className="truncate">
        {label}={value ? t("set", "gesetzt") : t("\u2014", "\u2014")}
      </span>
    </div>
  )
}

function Separator() {
  return <div className="border-t" />
}
