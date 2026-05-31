import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Loader2, Check, AlertTriangle } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import type { LibraryBrowsePaginatedResult } from "@/lib/tauri-bridge"

interface PreCheckPanelProps {
  sourceDirs: string[]
  targetRoot: string
  onComplete?: (result: PreCheckResult) => void
}

interface PreCheckResult {
  fileCount: number
  estimatedSize: number
  hasIssues: boolean
  issues: string[]
  duration: number
}

export function PreCheckPanel({ sourceDirs, targetRoot, onComplete }: PreCheckPanelProps) {
  const t = useT()
  const [state, setState] = useState<"idle" | "running" | "done" | "error">("idle")
  const [result, setResult] = useState<PreCheckResult | null>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!sourceDirs.length || state !== "idle") return
    runPreCheck()
  }, [sourceDirs])

  const runPreCheck = async () => {
    setState("running")
    const start = Date.now()

    try {
      const { libraryBrowsePaginated } = await import("@/lib/tauri-bridge")
      let totalFiles = 0
      const issues: string[] = []

      for (const dir of sourceDirs) {
        setProgress(p => p + 20)
        try {
          const r: LibraryBrowsePaginatedResult = await libraryBrowsePaginated({ root_dir: dir, page: 0, page_size: 1 })
          totalFiles += r.file_count
          if (r.other_count > 0) issues.push(`${r.other_count} non-media files in ${dir}`)
        } catch {
          issues.push(`Cannot access: ${dir}`)
        }
      }

      setProgress(90)

      if (targetRoot) {
        try {
          const r: LibraryBrowsePaginatedResult | null = await libraryBrowsePaginated({ root_dir: targetRoot, page: 0, page_size: 1 }).catch(() => null)
          if (r && r.file_count > 0) {
            issues.push("Target directory already contains files")
          }
        } catch {}
      }

      const res: PreCheckResult = {
        fileCount: totalFiles,
        estimatedSize: 0,
        hasIssues: issues.length > 0,
        issues,
        duration: (Date.now() - start) / 1000,
      }

      setResult(res)
      setState("done")
      setProgress(100)
      onComplete?.(res)
    } catch {
      setState("error")
    }
  }

  if (state === "idle") return null

  return (
    <Card className={result?.hasIssues ? "border-amber-200" : "border-green-200"}>
      <CardContent className="p-3">
        {state === "running" && (
          <div className="flex items-center gap-2 text-sm">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <span>{t("Scanning sources...", "Quellen werden gescannt...")}</span>
            <span className="text-xs text-muted-foreground ml-auto">{progress}%</span>
          </div>
        )}

        {state === "done" && result && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              {result.hasIssues ? (
                <AlertTriangle className="h-4 w-4 text-amber-500" />
              ) : (
                <Check className="h-4 w-4 text-green-500" />
              )}
              <span className="text-sm font-medium">
                {t("Pre-check complete", "Vorprüfung abgeschlossen")}
                <span className="text-xs text-muted-foreground ml-2">({result.duration}s)</span>
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded bg-muted/30">
                <p className="font-bold">{result.fileCount.toLocaleString()}</p>
                <p className="text-muted-foreground">{t("files", "Dateien")}</p>
              </div>
              <div className="p-2 rounded bg-muted/30">
                <p className="font-bold">{result.issues.length}</p>
                <p className="text-muted-foreground">{t("warnings", "Warnungen")}</p>
              </div>
            </div>
            {result.issues.slice(0, 3).map((issue, i) => (
              <p key={i} className="text-[10px] text-amber-600">• {issue}</p>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
