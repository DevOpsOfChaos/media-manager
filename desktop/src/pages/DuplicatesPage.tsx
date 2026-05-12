import { useState } from "react"
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
import { ErrorBanner } from "@/components/shared/ErrorBanner"
import { EmptyState } from "@/components/shared/EmptyState"
import { duplicateScan } from "@/lib/tauri-bridge"
import type { DuplicatesPreviewResponse } from "@/types"

export default function DuplicatesPage() {
  const [sourceDir, setSourceDir] = useState("")
  const [preview, setPreview] = useState<DuplicatesPreviewResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleScan = async () => {
    if (!sourceDir.trim()) {
      setError("Please select a source directory.")
      return
    }
    setLoading(true)
    setError(null)
    setPreview(null)
    try {
      const result = await duplicateScan({
        source_dirs: [sourceDir.trim()],
        include_patterns: [],
        exclude_patterns: [],
      })
      setPreview(result)
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  const browseForSource = async () => {
    try {
      const { open } = await import("@tauri-apps/plugin-dialog")
      const selected = await open({ directory: true, multiple: false, title: "Select source directory" })
      if (selected && typeof selected === "string") setSourceDir(selected)
    } catch { /* browser fallback */ }
  }

  const totalDupFiles =
    preview?.exact_groups.reduce((sum, g) => sum + g.files.length, 0) ?? 0
  const wastedCount = preview?.exact_duplicates ?? 0
  const wastedBytes =
    preview?.exact_groups.reduce(
      (sum, g) => sum + g.file_size * (g.files.length - 1),
      0,
    ) ?? 0

  return (
    <>
      <PageHeader title="Duplicates" />
      <main className="flex flex-1 gap-4 p-4">
        <div className="flex-1 max-w-4xl space-y-4">
          <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-950 px-4 py-3 text-sm text-blue-800 dark:text-blue-200">
            Preview only. No files are deleted or modified. Deletion will be
            available in a future update after review safeguards are in place.
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Find Duplicates</CardTitle>
              <CardDescription>
                Scan a folder for exact duplicate files by comparing file
                contents.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Source folder</label>
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="e.g. C:\Photos"
                    value={sourceDir}
                    onChange={(e) => setSourceDir(e.target.value)}
                    className="flex-1"
                  />
                  <Button variant="outline" size="sm" onClick={browseForSource}>
                    Browse...
                  </Button>
                </div>
              </div>

              <Button onClick={handleScan} disabled={loading} size="sm">
                {loading ? "Scanning..." : "Scan for duplicates"}
              </Button>
            </CardContent>
          </Card>

          {error && <ErrorBanner message={error} />}

          {preview && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <SummaryCard label="Scanned" value={preview.scanned_files} />
                <SummaryCard
                  label="Duplicate groups"
                  value={preview.exact_groups.length}
                  variant={
                    preview.exact_groups.length > 0 ? "default" : "secondary"
                  }
                />
                <SummaryCard label="Duplicate files" value={totalDupFiles} />
                <SummaryCard
                  label="Wasted copies"
                  value={wastedCount}
                  variant={wastedCount > 0 ? "destructive" : "secondary"}
                />
              </div>

              {wastedBytes > 0 && (
                <div className="rounded-lg border px-4 py-3 text-sm text-muted-foreground">
                  Estimated reclaimable space:{" "}
                  <span className="font-medium text-foreground">
                    {formatBytes(wastedBytes)}
                  </span>{" "}
                  ({wastedCount} copies of identical files)
                </div>
              )}

              {preview.exact_groups.length === 0 ? (
                <EmptyState
                  title="No duplicates found"
                  description="All scanned files are unique."
                />
              ) : (
                <Card>
                  <CardHeader>
                    <CardTitle>
                      Duplicate groups ({preview.exact_groups.length})
                    </CardTitle>
                    <CardDescription>
                      Groups of files with identical content.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-auto max-h-96">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b text-xs text-muted-foreground">
                            <th className="text-left px-4 py-2 font-medium">
                              Group
                            </th>
                            <th className="text-right px-4 py-2 font-medium">
                              Files
                            </th>
                            <th className="text-right px-4 py-2 font-medium">
                              Size
                            </th>
                            <th className="text-left px-4 py-2 font-medium">
                              Wasted
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {preview.exact_groups.slice(0, 100).map((g, i) => {
                            const wasted = g.file_size * (g.files.length - 1)
                            return (
                              <tr
                                key={`${g.full_digest.slice(0, 16)}-${i}`}
                                className="border-b last:border-0 hover:bg-muted/50"
                              >
                                <td className="px-4 py-1.5">
                                  <div className="space-y-0.5">
                                    {g.files.slice(0, 3).map((f) => (
                                      <p
                                        key={f}
                                        className="truncate font-mono text-xs max-w-[300px]"
                                      >
                                        {f}
                                      </p>
                                    ))}
                                    {g.files.length > 3 && (
                                      <p className="text-xs text-muted-foreground">
                                        +{g.files.length - 3} more
                                      </p>
                                    )}
                                  </div>
                                </td>
                                <td className="px-4 py-1.5 text-right tabular-nums text-xs">
                                  {g.files.length}
                                </td>
                                <td className="px-4 py-1.5 text-right tabular-nums text-xs text-muted-foreground">
                                  {formatBytes(g.file_size)}
                                </td>
                                <td className="px-4 py-1.5 text-xs text-destructive">
                                  {formatBytes(wasted)}
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                    {preview.exact_groups.length > 100 && (
                      <p className="px-4 py-2 text-xs text-muted-foreground">
                        Showing first 100 of {preview.exact_groups.length}{" "}
                        groups.
                      </p>
                    )}
                  </CardContent>
                </Card>
              )}

              <p className="text-xs text-muted-foreground">
                No files were deleted or modified. Deletion will be available in
                a future update.
              </p>
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

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B"
  const units = ["B", "KB", "MB", "GB"]
  const i = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1,
  )
  return `${(bytes / 1024 ** i).toFixed(i === 0 ? 0 : 1)} ${units[i]}`
}
