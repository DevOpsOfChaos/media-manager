import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import { useSimulatedProgress } from "@/lib/use-simulated-progress"
import { duplicateScan, similarImagesScan, duplicatesApply } from "@/lib/tauri-bridge"
import { userFriendlyError } from "@/lib/error-utils"
import { toast } from "@/lib/toast"
import { WizardContainer } from "@/components/shared/WizardContainer"
import { SourceDetector } from "@/components/shared/SourceDetector"
import { PreCheckPanel } from "@/components/shared/PreCheckPanel"
import { ExecutionProgress } from "@/components/shared/ExecutionProgress"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Check, RotateCcw, Scan, Trash2, ChevronRight, Zap } from "lucide-react"
import { ErrorBanner } from "@/components/shared/ErrorBanner"
import type { ExactDuplicateGroup } from "@/types"

const DUP_PHASES = [
  { nameEn: "Scanning files...", nameDe: "Dateien werden gescannt...", endAt: 15, increment: 1.5 },
  { nameEn: "Sample fingerprinting...", nameDe: "Sample-Fingerprinting...", endAt: 50, increment: 1 },
  { nameEn: "Full hashing...", nameDe: "Vollständiges Hashing...", endAt: 85, increment: 0.5 },
  { nameEn: "Byte comparison...", nameDe: "Byte-Vergleich...", endAt: 98, increment: 0.3 },
]

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

export default function DuplicatesPage() {
  const t = useT()
  const navigate = useNavigate()
  const { phase, progress, log, start: startSim, complete: completeSim } = useSimulatedProgress(DUP_PHASES)

  const [sourceDir, setSourceDir] = useState("")
  const [scanType, setScanType] = useState<"exact" | "similar" | "all">("exact")
  const [minSize, setMinSize] = useState("")
  const [maxSize, setMaxSize] = useState("")
  const [useFastMode, setUseFastMode] = useState(true)

  const [groups, setGroups] = useState<ExactDuplicateGroup[]>([])
  const [liveGroups, setLiveGroups] = useState<any[]>([])
  const [scanning, setScanning] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [decisions, setDecisions] = useState<Record<string, "keep" | "remove">>({})
  const [showSuccess, setShowSuccess] = useState(false)
  const [deletedCount, setDeletedCount] = useState(0)

  useEffect(() => {
    let unlisten: (() => void) | undefined
    const setup = async () => {
      const { listen } = await import("@tauri-apps/api/event")
      unlisten = await listen<any>("early-duplicate", (e) => {
        setLiveGroups((prev) => [...prev, e.payload])
      })
    }
    setup()
    return () => { unlisten?.() }
  }, [])

  const runScan = async () => {
    setScanning(true)
    setError(null)
    setGroups([])
    setLiveGroups([])
    startSim()
    try {
      const config = {
        source_dirs: [sourceDir],
        include_patterns: [] as string[],
        exclude_patterns: [] as string[],
        use_date_prefilter: useFastMode,
        fast: useFastMode,
      }

      if (scanType === "exact") {
        const r = await duplicateScan(config)
        completeSim()
        setGroups(r.exact_groups || [])
        toast("success", t(
          `Found ${r.exact_groups?.length || 0} duplicate groups`,
          `${r.exact_groups?.length || 0} Duplikatgruppen gefunden`
        ))
      } else if (scanType === "similar") {
        const r = await similarImagesScan({
          ...config,
          hash_size: 8,
          max_distance: 6,
          max_images: 500,
          max_pairs: 150_000,
        })
        completeSim()
        toast("info", t(
          `Found ${r.similar_groups?.length || 0} similar groups — review in Workbench`,
          `${r.similar_groups?.length || 0} ähnliche Gruppen — in der Workbench prüfen`
        ))
      } else {
        const [exact] = await Promise.all([
          duplicateScan(config),
          similarImagesScan({
            ...config,
            hash_size: 8,
            max_distance: 6,
            max_images: 500,
            max_pairs: 150_000,
          }),
        ])
        completeSim()
        setGroups(exact.exact_groups || [])
        toast("success", t(
          `Found ${exact.exact_groups?.length || 0} duplicate groups`,
          `${exact.exact_groups?.length || 0} Duplikatgruppen gefunden`
        ))
      }
    } catch (e: unknown) {
      setError(userFriendlyError(e).message || String(e))
      completeSim()
    } finally {
      setScanning(false)
    }
  }

  const handleApply = async () => {
    const toRemove = Object.entries(decisions).filter(([, v]) => v === "remove")
    if (toRemove.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const applyDecisions: Record<string, string> = {}
      for (const g of groups) {
        if (g.files.length <= 1) continue
        const keepFile = g.files.find((f) => decisions[f] !== "remove") || g.files[0]
        applyDecisions[`${g.file_size}:${g.full_digest}`] = keepFile
      }
      await duplicatesApply({ source_dirs: [sourceDir], decisions: applyDecisions, mode: "delete" })
      setDeletedCount(toRemove.length)
      setShowSuccess(true)
    } catch (e: unknown) {
      setError(userFriendlyError(e).message || String(e))
    } finally {
      setLoading(false)
    }
  }

  const autoDecide = () => {
    const d: Record<string, "keep" | "remove"> = {}
    for (const g of groups) {
      g.files.forEach((f: string, i: number) => {
        d[f] = i === 0 ? "keep" : "remove"
      })
    }
    setDecisions(d)
  }

  const startOver = () => {
    setShowSuccess(false)
    setGroups([])
    setLiveGroups([])
    setDecisions({})
    setDeletedCount(0)
  }

  const keepCount = Object.values(decisions).filter((v) => v === "keep").length
  const removeCount = Object.values(decisions).filter((v) => v === "remove").length

  if (showSuccess) {
    return (
      <div className="max-w-xl mx-auto p-6 text-center space-y-6">
        <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto">
          <Check className="h-10 w-10 text-green-600" />
        </div>
        <h2 className="text-xl font-bold">
          {t("Duplicates removed!", "Duplikate entfernt!")}
        </h2>
        <p className="text-muted-foreground">
          {deletedCount} {t("files deleted", "Dateien gelöscht")}
        </p>
        <div className="flex gap-2 justify-center">
          <Button variant="outline" onClick={startOver}>
            <RotateCcw className="h-4 w-4 mr-1" />
            {t("Scan again", "Erneut scannen")}
          </Button>
          <Button onClick={() => navigate("/library")}>
            {t("View Library", "Bibliothek ansehen")}
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </div>
    )
  }

  return (
    <WizardContainer
      steps={[
        { id: "source", label: "Select source", labelDe: "Quelle wählen" },
        { id: "scan", label: "Scan settings", labelDe: "Scan-Einstellungen" },
        { id: "results", label: "Results", labelDe: "Ergebnisse" },
        { id: "execute", label: "Execute", labelDe: "Ausführen" },
      ]}
    >
      {({ step, goNext, goBack, footer }) => (
        <>
          {error && <ErrorBanner message={error} />}
          {step === 0 && (
            <>
              <div className="text-center mb-6">
                <Scan className="h-12 w-12 text-primary mx-auto mb-3" />
                <h2 className="text-xl font-bold">
                  {t("Find duplicates", "Duplikate finden")}
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  {t(
                    "Free up disk space by finding and removing duplicate files.",
                    "Speicherplatz freigeben durch Finden und Entfernen doppelter Dateien."
                  )}
                </p>
              </div>
              <SourceDetector value={sourceDir} onChange={setSourceDir} showTarget={false} />
              <div className="mt-6">
                <Button className="w-full" size="lg" onClick={goNext} disabled={!sourceDir}>
                  {t("Next: Settings", "Weiter: Einstellungen")}{" "}
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
              {footer}
            </>
          )}

          {step === 1 && (
            <>
              <h2 className="text-lg font-semibold mb-4">
                {t("Scan settings", "Scan-Einstellungen")}
              </h2>
              <PreCheckPanel sourceDirs={[sourceDir]} targetRoot="" />
              <div className="mt-4 space-y-4">
                <div>
                  <label className="text-sm font-medium">
                    {t("Scan type", "Scan-Typ")}
                  </label>
                  <div className="flex gap-2 mt-1">
                    {(["exact", "similar", "all"] as const).map((type) => (
                      <button
                        key={type}
                        type="button"
                        onClick={() => setScanType(type)}
                        className={`flex-1 p-2 rounded-lg border text-sm transition-all ${
                          scanType === type
                            ? "border-primary bg-primary/5"
                            : "border-border hover:border-primary/30"
                        }`}
                      >
                        {type === "exact"
                          ? t("Exact", "Exakt")
                          : type === "similar"
                            ? t("Similar", "Ähnlich")
                            : t("All", "Alle")}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-muted-foreground">
                      {t("Min size (KB)", "Min Größe (KB)")}
                    </label>
                    <Input
                      value={minSize}
                      onChange={(e) => setMinSize(e.target.value)}
                      type="number"
                      className="text-xs"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-muted-foreground">
                      {t("Max size (KB)", "Max Größe (KB)")}
                    </label>
                    <Input
                      value={maxSize}
                      onChange={(e) => setMaxSize(e.target.value)}
                      type="number"
                      className="text-xs"
                      placeholder={t("Unlimited", "Unbegrenzt")}
                    />
                  </div>
                </div>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useFastMode}
                    onChange={(e) => setUseFastMode(e.target.checked)}
                  />
                  {t("Fast mode (date pre-filter)", "Schnellmodus (Datums-Vorfilter)")}
                </label>
              </div>
              <div className="flex gap-2 mt-6">
                <Button variant="outline" onClick={goBack}>
                  {t("Back", "Zurück")}
                </Button>
                <Button
                  className="flex-1"
                  onClick={() => {
                    runScan()
                    goNext()
                  }}
                  disabled={scanning}
                >
                  {scanning ? (
                    t("Scanning...", "Scanne...")
                  ) : (
                    <>
                      <Scan className="h-4 w-4 mr-1" />
                      {t("Start scan", "Scan starten")}
                    </>
                  )}
                </Button>
              </div>
              {footer}
            </>
          )}

          {step === 2 && (
            <>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  {t("Duplicate groups", "Duplikatgruppen")}
                </h2>
                <div className="flex gap-2">
                  {groups.length > 0 && (
                    <Button size="sm" variant="outline" onClick={autoDecide}>
                      {t("Auto-decide", "Auto-entscheiden")}
                    </Button>
                  )}
                  <Button size="sm" onClick={goNext} disabled={groups.length === 0}>
                    {t("Next: Execute", "Weiter: Ausführen")}{" "}
                    <ChevronRight className="h-3 w-3 ml-1" />
                  </Button>
                </div>
              </div>

              {scanning && (
                <ExecutionProgress
                  phase={phase}
                  totalPhases={4}
                  progress={progress}
                  log={log}
                  fileCount={liveGroups.length}
                  etaSeconds={0}
                  onMiniMode={() => {}}
                  toolName="duplicates"
                />
              )}

              {liveGroups.length > 0 && (
                <Card className="border-green-200 bg-green-50/30 mb-4">
                  <CardHeader className="pb-1">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Zap className="h-4 w-4 text-green-500" />
                      {t("Live results", "Live-Ergebnisse")} ({liveGroups.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="max-h-48 overflow-y-auto space-y-1">
                    {liveGroups.slice(-10).map((g, i) => (
                      <div key={i} className="text-xs flex items-center gap-2">
                        <Badge variant="secondary" className="text-[10px]">
                          {g.files?.length || 0} {t("dupes", "Dup.")}
                        </Badge>
                        <span className="text-muted-foreground">
                          {formatSize(g.file_size || 0)}
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {groups.map((g, i) => {
                  const wasted = g.file_size * ((g.files?.length || 1) - 1)
                  return (
                    <Card key={i} className="p-2">
                      <div className="flex items-center justify-between text-xs">
                        <Badge variant="secondary">
                          {g.files?.length || 0} {t("dupes", "Dup.")}
                        </Badge>
                        <span className="text-muted-foreground">
                          {formatSize(g.file_size || 0)}
                        </span>
                        <span className="text-red-500">
                          {formatSize(wasted)} {t("wasted", "verschwendet")}
                        </span>
                      </div>
                      {(g.files || []).slice(0, 5).map((f: string, j: number) => (
                        <div key={j} className="flex items-center gap-2 mt-1 text-[10px]">
                          <input
                            type="checkbox"
                            checked={decisions[f] !== "remove"}
                            onChange={(e) =>
                              setDecisions((d) => ({
                                ...d,
                                [f]: e.target.checked ? "keep" : "remove",
                              }))
                            }
                          />
                          <span className="truncate flex-1">{f.split(/[\\/]/).pop()}</span>
                        </div>
                      ))}
                      {g.files && g.files.length > 5 && (
                        <p className="text-[10px] text-muted-foreground mt-1">
                          +{g.files.length - 5} {t("more files", "weitere Dateien")}
                        </p>
                      )}
                    </Card>
                  )
                })}
                {groups.length === 0 && !scanning && (
                  <p className="text-center text-muted-foreground py-8">
                    {scanType === "similar"
                      ? t(
                          "Similar scan results are available in the Review Workbench.",
                          "Ähnlichkeits-Ergebnisse sind in der Prüf-Workbench verfügbar."
                        )
                      : t(
                          "No duplicates found — your library is clean!",
                          "Keine Duplikate gefunden — deine Bibliothek ist sauber!"
                        )}
                  </p>
                )}
              </div>
              {footer}
            </>
          )}

          {step === 3 && (
            <>
              <h2 className="text-lg font-semibold mb-4">
                {t("Execute", "Ausführen")}
              </h2>
              <div className="grid grid-cols-3 gap-2 mb-4">
                <Card className="text-center p-3">
                  <p className="text-xl font-bold text-green-600">{keepCount}</p>
                  <p className="text-[10px] text-muted-foreground">
                    {t("Keep", "Behalten")}
                  </p>
                </Card>
                <Card className="text-center p-3">
                  <p className="text-xl font-bold text-red-600">{removeCount}</p>
                  <p className="text-[10px] text-muted-foreground">
                    {t("Remove", "Entfernen")}
                  </p>
                </Card>
                <Card className="text-center p-3">
                  <p className="text-xl font-bold">{groups.length}</p>
                  <p className="text-[10px] text-muted-foreground">
                    {t("Groups", "Gruppen")}
                  </p>
                </Card>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={goBack}>
                  {t("Back", "Zurück")}
                </Button>
                <Button
                  variant="destructive"
                  className="flex-1"
                  onClick={handleApply}
                  disabled={removeCount === 0 || loading}
                >
                  <Trash2 className="h-4 w-4 mr-2" />{" "}
                  {t(`Delete ${removeCount} files`, `${removeCount} Dateien löschen`)}
                </Button>
              </div>
              {footer}
            </>
          )}
        </>
      )}
    </WizardContainer>
  )
}
