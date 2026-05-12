import { useState } from "react"
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

const DEFAULT_PATTERN = "{year}/{year_month_day}"

export default function OrganizePage() {
  const { options, setOptions } = useOrganizeStore()
  const [preview, setPreview] = useState<OrganizePreviewResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePreview = async () => {
    if (!options.source_dirs.length || !options.target_root) {
      setError("Source directory and target root are required.")
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

  return (
    <>
      <PageHeader title="Organize" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-4xl space-y-4">
          {/* Preview-only banner */}
          <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
            Preview only. No files are modified. The preview scans and plans
            without moving, copying, or deleting anything.
          </div>

          {/* Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
              <CardDescription>
                Set the source directory and target for the preview plan.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Source dir */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Source directory</label>
                <Input
                  type="text"
                  placeholder="e.g. C:\Photos\import"
                  value={
                    options.source_dirs.length > 0
                      ? options.source_dirs[0]
                      : ""
                  }
                  onChange={(e) =>
                    setOptions({
                      source_dirs: e.target.value ? [e.target.value] : [],
                    })
                  }
                />
              </div>

              {/* Target root */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Target root</label>
                <Input
                  type="text"
                  placeholder="e.g. C:\Photos\organized"
                  value={options.target_root}
                  onChange={(e) =>
                    setOptions({ target_root: e.target.value })
                  }
                />
              </div>

              {/* Pattern */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Pattern</label>
                <Input
                  type="text"
                  value={options.pattern || DEFAULT_PATTERN}
                  onChange={(e) => setOptions({ pattern: e.target.value })}
                />
                <p className="text-xs text-muted-foreground">
                  Tokens: {"{year}"}, {"{month}"}, {"{day}"},{" "}
                  {"{year_month}"}, {"{year_month_day}"}, {"{source_name}"}
                </p>
              </div>

              {/* Operation mode */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Operation mode</label>
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
                      {mode === "copy" ? "Copy" : "Move"}
                    </label>
                  ))}
                </div>
              </div>

              {/* Conflict policy */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Conflict policy</label>
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
                      {policy === "conflict" ? "Flag conflict" : "Skip"}
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Preview button */}
          <div className="flex items-center gap-3">
            <Button onClick={handlePreview} disabled={loading} size="sm">
              {loading ? "Generating preview..." : "Preview plan"}
            </Button>
            {error && (
              <p className="text-sm text-destructive truncate">{error}</p>
            )}
          </div>

          {/* Results */}
          {preview && (
            <>
              {/* Summary cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <SummaryCard
                  label="Media files"
                  value={preview.media_file_count}
                />
                <SummaryCard
                  label="Planned"
                  value={preview.planned_count}
                  variant="default"
                />
                <SummaryCard
                  label="Skipped"
                  value={preview.skipped_count}
                  variant="secondary"
                />
                <SummaryCard
                  label="Conflicts"
                  value={preview.conflict_count}
                  variant={
                    preview.conflict_count > 0 ? "destructive" : "secondary"
                  }
                />
              </div>

              {/* Missing sources */}
              {preview.scan_summary.missing_sources.length > 0 && (
                <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  <p className="font-medium">Missing sources</p>
                  {preview.scan_summary.missing_sources.map((s) => (
                    <p key={s} className="truncate font-mono text-xs">
                      {s}
                    </p>
                  ))}
                </div>
              )}

              {/* Outcome */}
              {oc && (
                <Card>
                  <CardHeader>
                    <CardTitle>Plan outcome</CardTitle>
                    <CardDescription>{oc.next_action}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2 text-sm">
                      <Badge
                        variant={
                          oc.safe_to_apply ? "default" : "destructive"
                        }
                      >
                        {oc.safe_to_apply ? "Safe to apply" : "Needs review"}
                      </Badge>
                      <Badge variant="secondary">
                        {oc.status.replace(/_/g, " ")}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {oc.total_count} total  /  {oc.actionable_count}{" "}
                        actionable  /  {oc.blocked_count} blocked
                      </span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Entries table */}
              {preview.entries.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>
                      Entries ({preview.entries.length})
                    </CardTitle>
                    <CardDescription>
                      Files that would be organized.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-auto max-h-96">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b text-xs text-muted-foreground">
                            <th className="text-left px-4 py-2 font-medium">
                              Source
                            </th>
                            <th className="text-left px-4 py-2 font-medium">
                              Target
                            </th>
                            <th className="text-left px-4 py-2 font-medium">
                              Status
                            </th>
                            <th className="text-left px-4 py-2 font-medium">
                              Reason
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
                        Showing first 200 of {preview.entries.length} entries.
                      </p>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Empty entries */}
              {preview.entries.length === 0 && (
                <Card>
                  <CardContent className="py-8 text-center text-sm text-muted-foreground">
                    No files found to organize in the source directory.
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
