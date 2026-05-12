import { useState, useMemo } from "react"
import { PageHeader } from "@/components/layout/PageHeader"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { organizePreview } from "@/lib/tauri-bridge"
import type { OrganizePreviewResponse } from "@/types"
import { useOrganizeStore } from "@/stores/organize-store"
import { useSettingsStore } from "@/stores/settings-store"

// ── Pattern presets ──

interface Preset {
  id: string
  label: string
  labelDe: string
  pattern: string
  example: (lang: string) => string
}

// File names are always preserved automatically by the backend.
// The pattern controls only the folder structure.
// Examples show the full result: folder structure + auto file name.
const PRESETS: Preset[] = [
  {
    id: "year-month",
    label: "Year / Month",
    labelDe: "Jahr / Monat",
    pattern: "{year}/{year_month}",
    example: () => "2026/2026-05/DSC_0001.jpg",
  },
  {
    id: "year-monthname",
    label: "Year / Month name",
    labelDe: "Jahr / Monatsname",
    pattern: `{year}/{month_name}`,
    example: (lang) =>
      lang === "de"
        ? "2026/Mai/DSC_0001.jpg"
        : "2026/May/DSC_0001.jpg",
  },
  {
    id: "year-monthname-de",
    label: "Year / Month name (German)",
    labelDe: "Jahr / Monatsname (Deutsch)",
    pattern: `{year}/{month_name_de}`,
    example: () => "2026/Mai/DSC_0001.jpg",
  },
  {
    id: "year-monthday",
    label: "Year / Year-Month-Day",
    labelDe: "Jahr / Jahr-Monat-Tag",
    pattern: "{year}/{year_month_day}",
    example: () => "2026/2026-05-12/DSC_0001.jpg",
  },
  {
    id: "flat-year-month-day",
    label: "Flat: Year-Month-Day",
    labelDe: "Flach: Jahr-Monat-Tag",
    pattern: "{year_month_day}",
    example: () => "2026-05-12/DSC_0001.jpg",
  },
]

// ── Token builder ──

interface TokenDef {
  token: string
  label: string
  labelDe: string
}

const TOKENS: TokenDef[] = [
  { token: "{year}", label: "Year", labelDe: "Jahr" },
  { token: "{month}", label: "Month (01–12)", labelDe: "Monat (01–12)" },
  {
    token: "{month_name}",
    label: "Month name (English)",
    labelDe: "Monatsname (Englisch)",
  },
  {
    token: "{month_name_de}",
    label: "Month name (German)",
    labelDe: "Monatsname (Deutsch)",
  },
  { token: "{day}", label: "Day (01–31)", labelDe: "Tag (01–31)" },
  {
    token: "{year_month}",
    label: "Year-Month (2026-05)",
    labelDe: "Jahr-Monat (2026-05)",
  },
  {
    token: "{year_month_day}",
    label: "Year-Month-Day (2026-05-12)",
    labelDe: "Jahr-Monat-Tag (2026-05-12)",
  },
  { token: "{source_name}", label: "Source folder name (e.g. \"Import\")", labelDe: "Quellordner-Name (z.B. \"Import\")" },
]

const SEPARATORS = [
  { char: " - ", label: "Dash" },
  { char: "_", label: "Underscore _ " },
  { char: " ", label: "Space" },
]

// ── Month names ──

const MONTHS_DE = [
  "Januar", "Februar", "März", "April", "Mai", "Juni",
  "Juli", "August", "September", "Oktober", "November", "Dezember",
]
const MONTHS_EN = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
]

// ── Live example generator ──

function buildLiveExample(pattern: string): string {
  const now = new Date()
  const year = String(now.getFullYear())
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const monthNameEn = MONTHS_EN[now.getMonth()]
  const monthNameDe = MONTHS_DE[now.getMonth()]
  const day = String(now.getDate()).padStart(2, "0")
  const yearMonth = `${year}-${month}`
  const yearMonthDay = `${year}-${month}-${day}`

  const rendered = pattern
    .replace(/{year}/g, year)
    .replace(/{month}/g, month)
    .replace(/{month_name}/g, monthNameEn)
    .replace(/{month_name_de}/g, monthNameDe)
    .replace(/{day}/g, day)
    .replace(/{year_month}/g, yearMonth)
    .replace(/{year_month_day}/g, yearMonthDay)
    .replace(/{source_name}/g, "Import")
  // File names are always preserved automatically
  return `${rendered}/DSC_0001.jpg`
}

// ── Main component ──

export default function OrganizePage() {
  const { options, setOptions } = useOrganizeStore()
  const { settings } = useSettingsStore()
  const lang = settings.language === "de" ? "de" : "en"

  const [preview, setPreview] = useState<OrganizePreviewResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedPreset, setSelectedPreset] = useState<string>("year-month")
  const [showCustomPattern, setShowCustomPattern] = useState(false)

  const t = <T extends string>(en: T, de: T): T => (lang === "de" ? de : en)

  // Keep source_dirs as a single string in the store but display as text input
  const sourceDir =
    options.source_dirs.length > 0 ? options.source_dirs[0] : ""

  // Apply a preset
  const applyPreset = (presetId: string) => {
    setSelectedPreset(presetId)
    if (presetId === "custom") {
      setShowCustomPattern(true)
      return
    }
    setShowCustomPattern(false)
    const preset = PRESETS.find((p) => p.id === presetId)
    if (preset) {
      setOptions({ pattern: preset.pattern })
    }
  }

  // Native directory picker (Tauri-only, graceful fallback)
  const browseDirectory = async (
    target: "source" | "target",
  ) => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog")
      const selected = await open({ directory: true, multiple: false, title: target === "source" ? "Select source directory" : "Select target directory" })
      if (selected && typeof selected === "string") {
        if (target === "source") {
          setOptions({ source_dirs: [selected] })
        } else {
          setOptions({ target_root: selected })
        }
      }
    } catch {
      // Fallback: Tauri APIs unavailable (e.g. running in browser)
      // Text input remains usable.
    }
  }

  const handlePreview = async () => {
    if (!sourceDir || !options.target_root) {
      setError(
        t(
          "Please select a source directory and a target root.",
          "Bitte wählen Sie ein Quellverzeichnis und ein Zielverzeichnis.",
        ),
      )
      return
    }
    setLoading(true)
    setError(null)
    setPreview(null)
    try {
      const result = await organizePreview(options)
      setPreview(result)
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  const oc = preview?.outcome_report

  // Build live example from current pattern
  const liveExample = useMemo(
    () => buildLiveExample(options.pattern || "{year}/{year_month_day}"),
    [options.pattern],
  )

  return (
    <>
      <PageHeader title={t("Organize", "Organisieren")} />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-4xl space-y-4">
          {/* Safety banner */}
          <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
            <p className="font-medium">
              {t(
                "Preview only. No files are modified.",
                "Nur Vorschau. Es werden keine Dateien verändert.",
              )}
            </p>
            <p className="text-xs mt-0.5">
              {t(
                "The preview shows what would happen. Apply will be available in a future update after review safeguards are in place.",
                "Die Vorschau zeigt, was passieren würde. Die Ausführung wird in einem zukünftigen Update verfügbar sein, sobald Prüf- und Sicherheitsmechanismen integriert sind.",
              )}
            </p>
          </div>

          {/* Step 1: Directories */}
          <Card>
            <CardHeader>
              <CardTitle>
                {t("1. Select directories", "1. Verzeichnisse wählen")}
              </CardTitle>
              <CardDescription>
                {t(
                  "Choose the source folder with your media files and where they should be organized.",
                  "Wählen Sie den Quellordner mit Ihren Mediendateien und das Ziel für die organisierte Ablage.",
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">
                  {t("Source folder", "Quellordner")}
                </label>
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder={
                      lang === "de"
                        ? "z.B. C:\\Fotos\\Import"
                        : "e.g. C:\\Photos\\import"
                    }
                    value={sourceDir}
                    onChange={(e) =>
                      setOptions({
                        source_dirs: e.target.value ? [e.target.value] : [],
                      })
                    }
                    className="flex-1"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => browseDirectory("source")}
                  >
                    {t("Browse...", "Durchsuchen...")}
                  </Button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">
                  {t("Target folder", "Zielordner")}
                </label>
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder={
                      lang === "de"
                        ? "z.B. C:\\Fotos\\Organisiert"
                        : "e.g. C:\\Photos\\organized"
                    }
                    value={options.target_root}
                    onChange={(e) =>
                      setOptions({ target_root: e.target.value })
                    }
                    className="flex-1"
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => browseDirectory("target")}
                  >
                    {t("Browse...", "Durchsuchen...")}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Step 2: Pattern */}
          <Card>
            <CardHeader>
              <CardTitle>
                {t("2. Choose folder structure", "2. Ordnerstruktur wählen")}
              </CardTitle>
              <CardDescription>
                {t(
                  "How should files be organized into folders? Original file names are always preserved.",
                  "Wie sollen die Dateien in Ordner einsortiert werden? Die ursprünglichen Dateinamen bleiben immer erhalten.",
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Presets */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => applyPreset(preset.id)}
                    className={`rounded-lg border p-3 text-left transition-colors ${
                      selectedPreset === preset.id && !showCustomPattern
                        ? "border-primary bg-primary/5 ring-1 ring-primary"
                        : "hover:bg-muted/50"
                    }`}
                  >
                    <p className="text-sm font-medium">
                      {lang === "de" ? preset.labelDe : preset.label}
                    </p>
                    <p className="text-xs text-muted-foreground font-mono mt-0.5">
                      {preset.example(lang)}
                    </p>
                  </button>
                ))}
                <button
                  onClick={() => applyPreset("custom")}
                  className={`rounded-lg border p-3 text-left transition-colors ${
                    showCustomPattern
                      ? "border-primary bg-primary/5 ring-1 ring-primary"
                      : "hover:bg-muted/50"
                  }`}
                >
                  <p className="text-sm font-medium">
                    {t("Custom pattern", "Eigenes Muster")}
                  </p>
                  <p className="text-xs text-muted-foreground font-mono mt-0.5">
                    {liveExample}
                  </p>
                </button>
              </div>

              {/* Custom pattern builder */}
              {showCustomPattern && (
                <div className="space-y-3 rounded-lg border p-4 bg-muted/20">
                  <p className="text-xs text-muted-foreground">
                    {t(
                      "File names are always preserved automatically. The pattern only controls folder structure.",
                      "Dateinamen bleiben immer automatisch erhalten. Das Muster steuert nur die Ordnerstruktur.",
                    )}
                  </p>

                  {/* Tokens */}
                  <div className="flex flex-wrap gap-1.5">
                    {TOKENS.map((tok) => {
                      const isActive = options.pattern?.includes(tok.token)
                      return (
                        <button
                          key={tok.token}
                          onClick={() => {
                            const current = options.pattern || ""
                            const next = current
                              ? (current.endsWith("/") || current.endsWith(" ") || current.endsWith("_") || current.endsWith("-")
                                  ? `${current}${tok.token}`
                                  : `${current}/${tok.token}`)
                              : tok.token
                            setOptions({ pattern: next })
                          }}
                          className={`inline-flex items-center rounded-md border px-2 py-1 text-xs transition-colors ${
                            isActive
                              ? "border-primary bg-primary/10 text-primary"
                              : "hover:bg-muted"
                          }`}
                        >
                          {lang === "de" ? tok.labelDe : tok.label}
                        </button>
                      )
                    })}
                  </div>

                  {/* Separators */}
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs text-muted-foreground">
                      {t("Separator:", "Trennzeichen:")}
                    </span>
                    {SEPARATORS.map((sep) => (
                      <button
                        key={sep.char}
                        onClick={() => {
                          const current = options.pattern || ""
                          setOptions({ pattern: current + sep.char })
                        }}
                        className="inline-flex items-center rounded-md border px-2 py-1 text-xs hover:bg-muted transition-colors"
                      >
                        {sep.label}
                      </button>
                    ))}
                  </div>

                  {/* Clear */}
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setOptions({ pattern: "" })}
                    >
                      {t("Clear pattern", "Muster leeren")}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setOptions({ pattern: "{year}/{year_month_day}" })
                      }
                    >
                      {t("Reset to default", "Auf Standard zurücksetzen")}
                    </Button>
                  </div>

                  {/* Live preview */}
                  <div className="rounded-md border bg-background px-3 py-2">
                    <p className="text-xs text-muted-foreground">
                      {t("Live preview:", "Live-Vorschau:")}
                    </p>
                    <p className="text-sm font-mono">{liveExample}</p>
                  </div>

                  {/* Advanced: raw pattern */}
                  <div className="space-y-1">
                    <label className="text-xs text-muted-foreground">
                      {t(
                        "Advanced: raw pattern",
                        "Erweitert: Roh-Muster",
                      )}
                    </label>
                    <Input
                      type="text"
                      value={options.pattern || ""}
                      onChange={(e) =>
                        setOptions({ pattern: e.target.value })
                      }
                      className="h-8 font-mono text-xs"
                    />
                  </div>
                </div>
              )}

              {/* Always show live preview for current pattern */}
              {!showCustomPattern && (
                <div className="rounded-md border bg-background px-3 py-2">
                  <p className="text-xs text-muted-foreground">
                    {t("Example:", "Beispiel:")}
                  </p>
                  <p className="text-sm font-mono">{liveExample}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Step 3: Options */}
          <Card>
            <CardHeader>
              <CardTitle>
                {t("3. Options", "3. Optionen")}
              </CardTitle>
              <CardDescription>
                {t(
                  "Configure file handling and behavior.",
                  "Legen Sie fest, wie mit Dateien umgegangen wird.",
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">
                  {t("What should happen?", "Was soll passieren?")}
                </label>
                <div className="flex gap-3">
                  {(["copy", "move"] as const).map((mode) => (
                    <label
                      key={mode}
                      className="flex items-center gap-1.5 text-sm"
                    >
                      <input
                        type="radio"
                        name="operation_mode"
                        value={mode}
                        checked={options.operation_mode === mode}
                        onChange={() =>
                          setOptions({ operation_mode: mode })
                        }
                      />
                      {mode === "copy"
                        ? t(
                            "Copy files (safe preview)",
                            "Dateien kopieren (sichere Vorschau)",
                          )
                        : t(
                            "Move files (not yet available)",
                            "Dateien verschieben (noch nicht verfügbar)",
                          )}
                    </label>
                  ))}
                </div>
                {options.operation_mode === "move" && (
                  <p className="text-xs text-muted-foreground ml-6">
                    {t(
                      "Move is currently preview-only. No files will be moved.",
                      "Verschieben ist derzeit nur eine Vorschau. Es werden keine Dateien verschoben.",
                    )}
                  </p>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">
                  {t(
                    "What if a file already exists?",
                    "Was passiert bei gleichem Dateinamen?",
                  )}
                </label>
                <div className="flex gap-3">
                  {(["conflict", "skip"] as const).map((policy) => (
                    <label
                      key={policy}
                      className="flex items-center gap-1.5 text-sm"
                    >
                      <input
                        type="radio"
                        name="conflict_policy"
                        value={policy}
                        checked={options.conflict_policy === policy}
                        onChange={() =>
                          setOptions({ conflict_policy: policy })
                        }
                      />
                      {policy === "conflict"
                        ? t("Flag as conflict", "Als Konflikt markieren")
                        : t("Skip existing", "Vorhandene überspringen")}
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Preview button */}
          <div className="flex items-center gap-3">
            <Button onClick={handlePreview} disabled={loading} size="sm">
              {loading
                ? t(
                    "Generating preview...",
                    "Vorschau wird erstellt...",
                  )
                : t("Preview plan", "Vorschau erstellen")}
            </Button>
            {error && (
              <p className="text-sm text-destructive truncate">{error}</p>
            )}
          </div>

          {/* Results */}
          {preview && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                <SummaryCard
                  label={t("Scanned", "Gefunden")}
                  value={preview.media_file_count}
                />
                <SummaryCard
                  label={t("Planned", "Geplant")}
                  value={preview.planned_count}
                  variant="default"
                />
                <SummaryCard
                  label={t("Skipped", "Übersprungen")}
                  value={preview.skipped_count}
                  variant="secondary"
                />
                <SummaryCard
                  label={t("Conflicts", "Konflikte")}
                  value={preview.conflict_count}
                  variant={
                    preview.conflict_count > 0 ? "destructive" : "secondary"
                  }
                />
                <SummaryCard
                  label={t("Errors", "Fehler")}
                  value={preview.error_count}
                  variant={preview.error_count > 0 ? "destructive" : "secondary"}
                />
              </div>

              {preview.scan_summary.missing_sources.length > 0 && (
                <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  <p className="font-medium">
                    {t("Missing sources", "Fehlende Quellen")}
                  </p>
                  {preview.scan_summary.missing_sources.map((s) => (
                    <p key={s} className="truncate font-mono text-xs">
                      {s}
                    </p>
                  ))}
                </div>
              )}

              {oc && (
                <Card>
                  <CardHeader>
                    <CardTitle>
                      {t("Result", "Ergebnis")}
                    </CardTitle>
                    <CardDescription>
                      {t(oc.next_action, oc.next_action)}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2 text-sm">
                      <Badge
                        variant={
                          oc.safe_to_apply ? "default" : "destructive"
                        }
                      >
                        {oc.safe_to_apply
                          ? t("Safe to apply", "Bereit zur Ausführung")
                          : t("Needs review", "Prüfung erforderlich")}
                      </Badge>
                      <Badge variant="secondary">
                        {oc.status.replace(/_/g, " ")}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {oc.total_count}{" "}
                        {t("total", "gesamt")} / {oc.actionable_count}{" "}
                        {t("actionable", "ausführbar")} /{" "}
                        {oc.blocked_count}{" "}
                        {t("blocked", "blockiert")}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {preview.entries.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>
                      {t("File list", "Dateiliste")} ({preview.entries.length})
                    </CardTitle>
                    <CardDescription>
                      {t(
                        "Files that would be organized.",
                        "Dateien, die organisiert werden würden.",
                      )}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-auto max-h-96">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b text-xs text-muted-foreground">
                            <th className="text-left px-4 py-2 font-medium">
                              {t("Source", "Quelle")}
                            </th>
                            <th className="text-left px-4 py-2 font-medium">
                              {t("Target", "Ziel")}
                            </th>
                            <th className="text-left px-4 py-2 font-medium">
                              {t("Action", "Aktion")}
                            </th>
                            <th className="text-left px-4 py-2 font-medium">
                              {t("Note", "Hinweis")}
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {preview.entries.slice(0, 200).map((e, i) => (
                            <tr
                              key={`${e.source_path}-${i}`}
                              className="border-b last:border-0 hover:bg-muted/50"
                            >
                              <td className="px-4 py-1.5 truncate max-w-[200px] font-mono text-xs">
                                {e.relative_source_path}
                              </td>
                              <td className="px-4 py-1.5 truncate max-w-[200px] font-mono text-xs text-muted-foreground">
                                {e.target_relative_dir ?? "—"}
                              </td>
                              <td className="px-4 py-1.5">
                                <Badge
                                  variant={
                                    e.status === "planned"
                                      ? "default"
                                      : e.status === "conflict"
                                        ? "destructive"
                                        : "secondary"
                                  }
                                >
                                  {e.status}
                                </Badge>
                              </td>
                              <td className="px-4 py-1.5 text-xs text-muted-foreground truncate max-w-[150px]">
                                {e.reason}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {preview.entries.length > 200 && (
                      <p className="px-4 py-2 text-xs text-muted-foreground">
                        {t(
                          `Showing first 200 of ${preview.entries.length} entries.`,
                          `Zeige erste 200 von ${preview.entries.length} Einträgen.`,
                        )}
                      </p>
                    )}
                  </CardContent>
                </Card>
              )}

              {preview.entries.length === 0 && (
                <Card>
                  <CardContent className="py-8 text-center text-sm text-muted-foreground">
                    {t(
                      "No files found to organize in the source directory.",
                      "Keine Dateien zum Organisieren im Quellverzeichnis gefunden.",
                    )}
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </main>
    </>
  )
}

function SummaryCard({
  label,
  value,
  variant = "default",
}: {
  label: string
  value: number
  variant?: "default" | "secondary" | "destructive"
}) {
  const colorClass =
    variant === "destructive"
      ? "text-destructive"
      : variant === "secondary"
        ? "text-muted-foreground"
        : "text-foreground"
  return (
    <div className="rounded-lg border p-3 text-center">
      <p className="text-2xl font-bold tabular-nums">{value}</p>
      <p className={`text-xs ${colorClass}`}>{label}</p>
    </div>
  )
}
