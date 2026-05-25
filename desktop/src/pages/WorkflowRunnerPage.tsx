import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { organizePreview, organizeApply, duplicateScan, duplicatesApply, libraryBrowse, peopleScan, tripApply } from "@/lib/tauri-bridge"
import type { DuplicatesPreviewResponse } from "@/types"
import { PreflightCheck } from "@/components/shared/PreflightCheck"
import { Workflow, Play, CheckCircle2, Loader2, XCircle } from "lucide-react"
import { open } from "@tauri-apps/plugin-dialog"

type StepStatus = "pending" | "running" | "done" | "error" | "skipped"

interface WorkflowStep {
  key: string
  label: string
  status: StepStatus
  summary?: string
}

export default function WorkflowRunnerPage() {
  const [sourceDir, setSourceDir] = useState(() => localStorage.getItem("default_source_dir") || "")
  const [targetDir, setTargetDir] = useState("")
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [includePeople, setIncludePeople] = useState(false)
  const [includeTrip, setIncludeTrip] = useState(false)

  const browseDir = useCallback(async (setter: (v: string) => void) => {
    try {
      const selected = await open({ directory: true, multiple: false, title: "Select directory" })
      if (selected && typeof selected === "string") setter(selected)
    } catch { /* dialog may not be available */ }
  }, [])

  const [steps, setSteps] = useState<WorkflowStep[]>([
    { key: "organize", label: "Organize Files", status: "pending" },
    { key: "duplicates", label: "Find Duplicates", status: "pending" },
    { key: "leftovers", label: "Consolidate Leftovers", status: "pending" },
  ])

  const updateStep = (key: string, update: Partial<WorkflowStep>) => {
    setSteps(prev => prev.map(s => s.key === key ? { ...s, ...update } : s))
  }

  const runWorkflow = useCallback(async () => {
    if (!sourceDir || !targetDir) return
    setRunning(true)
    setError(null)

    const allSteps = [...steps]
    if (includePeople) allSteps.push({ key: "people", label: "People Scan", status: "pending" })
    if (includeTrip) allSteps.push({ key: "trip", label: "Trip Collection", status: "pending" })

    const options = {
      source_dirs: [sourceDir],
      target_root: targetDir,
      pattern: "{year}/{year_month_day}",
      recursive: true,
      include_hidden: false,
      follow_symlinks: false,
      operation_mode: "copy" as const,
      exiftool_path: null,
      include_associated_files: true,
      conflict_policy: "conflict" as const,
      include_patterns: [] as string[],
      exclude_patterns: [] as string[],
      batch_size: 0,
    }

    // Step 1: Organize
    updateStep("organize", { status: "running" })
    try {
      const plan = await organizePreview(options)
      if (plan.planned_count > 0) {
        const result = await organizeApply(options)
        updateStep("organize", {
          status: "done",
          summary: `${result.executed_count} files organized (${result.copied_count} copied, ${result.moved_count} moved)`,
        })
      } else {
        updateStep("organize", { status: "skipped", summary: "No files to organize" })
      }
    } catch (e) {
      updateStep("organize", { status: "error", summary: String(e) })
      setRunning(false)
      return
    }

    // Step 3: Duplicates
    updateStep("duplicates", { status: "running" })
    try {
      const dupResult = await duplicateScan({
        source_dirs: [targetDir],
        include_patterns: [],
        exclude_patterns: [],
      })
      const groups = (dupResult as DuplicatesPreviewResponse).exact_groups || []
      if (groups.length > 0) {
        const decisions: Record<string, string> = {}
        for (const g of groups) {
          if (g.files.length > 1) {
            decisions[`${g.file_size}:${g.full_digest}`] = g.files[0]
          }
        }
        if (Object.keys(decisions).length > 0) {
          const delResult = await duplicatesApply({
            source_dirs: [targetDir],
            decisions,
            mode: "delete",
          })
          updateStep("duplicates", {
            status: "done",
            summary: `${delResult.executed_rows} duplicate groups removed`,
          })
        } else {
          updateStep("duplicates", { status: "skipped", summary: "No duplicates to remove" })
        }
      } else {
        updateStep("duplicates", { status: "skipped", summary: "No duplicates found" })
      }
    } catch (e) {
      updateStep("duplicates", { status: "error", summary: String(e) })
    }

    // Step 4: Leftovers
    updateStep("leftovers", { status: "running" })
    try {
      const lib = await libraryBrowse({ root_dir: sourceDir, max_depth: 1 })
      const remaining = lib.files.filter(f => {
        const rel = f.relative.replace(/\\/g, "/")
        return !rel.includes("/")
      })
      if (remaining.length > 0) {
        updateStep("leftovers", {
          status: "done",
          summary: `${remaining.length} files remain in source. Use Organize page with --consolidate-leftovers.`,
        })
      } else {
        updateStep("leftovers", { status: "done", summary: "No leftover files found" })
      }
    } catch {
      updateStep("leftovers", { status: "done", summary: "Leftover check complete" })
    }

    // Optional: People scan
    if (includePeople) {
      updateStep("people", { status: "running" })
      try {
        await peopleScan({ source_dirs: [targetDir], incremental: false, force_full: true })
        updateStep("people", { status: "done", summary: "Face scan complete" })
      } catch (e) {
        updateStep("people", { status: "error", summary: String(e) })
      }
    }

    // Optional: Trip
    if (includeTrip) {
      updateStep("trip", { status: "running" })
      try {
        const today = new Date().toISOString().split("T")[0]
        await tripApply({
          source_dirs: [targetDir],
          target_root: targetDir + "/_trips",
          label: "auto_trip_" + today,
          start_date: today,
          end_date: today,
          use_hardlinks: true,
        })
        updateStep("trip", { status: "done", summary: "Trip created" })
      } catch (e) {
        updateStep("trip", { status: "error", summary: String(e) })
      }
    }

    setRunning(false)
  }, [sourceDir, targetDir])

  const statusIcon = (status: StepStatus) => {
    switch (status) {
      case "running": return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
      case "done": return <CheckCircle2 className="w-4 h-4 text-green-400" />
      case "error": return <XCircle className="w-4 h-4 text-red-400" />
      case "skipped": return <CheckCircle2 className="w-4 h-4 text-muted-foreground" />
      default: return <div className="w-4 h-4 rounded-full border-2 border-muted" />
    }
  }

  const allDone = steps.every(s => s.status === "done" || s.status === "skipped")

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Workflow className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-xl font-bold">Workflow Runner</h1>
          <p className="text-sm text-muted-foreground">Run organize → duplicates → leftovers in sequence.</p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Source & Target</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-1">
            <span className="text-xs font-medium">Source Directory</span>
            <div className="flex gap-1">
              <Input value={sourceDir} onChange={e => setSourceDir(e.target.value)} placeholder="C:\Photos" className="text-xs flex-1" disabled={running} />
              <Button variant="outline" size="sm" className="text-xs h-8" onClick={() => browseDir(setSourceDir)} disabled={running}>Browse</Button>
            </div>
          </div>
          <div className="space-y-1">
            <span className="text-xs font-medium">Target Directory</span>
            <div className="flex gap-1">
              <Input value={targetDir} onChange={e => setTargetDir(e.target.value)} placeholder="C:\Organized" className="text-xs flex-1" disabled={running} />
              <Button variant="outline" size="sm" className="text-xs h-8" onClick={() => browseDir(setTargetDir)} disabled={running}>Browse</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Optional Steps</CardTitle></CardHeader>
        <CardContent className="space-y-2">
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" checked={includePeople} onChange={e => setIncludePeople(e.target.checked)} className="w-4 h-4" />
            <span>People Scan</span>
            <span className="text-xs text-muted-foreground">— Scan for faces after organizing</span>
          </label>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" checked={includeTrip} onChange={e => setIncludeTrip(e.target.checked)} className="w-4 h-4" />
            <span>Trip Collection</span>
            <span className="text-xs text-muted-foreground">— Create trip from date range (requires label + dates)</span>
          </label>
        </CardContent>
      </Card>

      <PreflightCheck sourceDirs={sourceDir ? [sourceDir] : []} targetRoot={targetDir} />

      <Button
        onClick={runWorkflow}
        disabled={running || !sourceDir || !targetDir}
        size="sm"
        className="w-full"
      >
        {running ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Running workflow...</> : <><Play className="w-4 h-4 mr-2" /> Run Full Workflow</>}
      </Button>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <Card className={allDone ? "border-green-500/30" : ""}>
        <CardHeader><CardTitle className="text-sm">Progress</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {steps.map(step => (
            <div key={step.key} className="flex items-center gap-3 p-2 rounded bg-muted/30">
              {statusIcon(step.status)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{step.label}</p>
                {step.summary && <p className="text-xs text-muted-foreground truncate">{step.summary}</p>}
              </div>
              <Badge variant={step.status === "done" ? "default" : step.status === "error" ? "destructive" : "secondary"} className="text-xs">
                {step.status}
              </Badge>
            </div>
          ))}
        </CardContent>
      </Card>

      {allDone && (
        <Card className="border-green-500/30">
          <CardHeader><CardTitle className="text-sm text-green-400">Workflow Complete</CardTitle></CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              All steps finished. Check History for undo options or run another workflow.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
