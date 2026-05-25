import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { doctorCheck, type DoctorReport } from "@/lib/tauri-bridge"
import { CheckCircle, AlertTriangle, XCircle, Loader2, Stethoscope } from "lucide-react"

interface PreflightCheckProps {
  sourceDirs: string[]
  targetRoot?: string
  command?: string
  onReady?: (report: DoctorReport) => void
}

export function PreflightCheck({ sourceDirs, targetRoot, command = "organize" }: PreflightCheckProps) {
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<DoctorReport | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runCheck = async () => {
    if (sourceDirs.length === 0) return
    setLoading(true)
    setError(null)
    try {
      const result = await doctorCheck({
        command,
        source_dirs: sourceDirs,
        target_root: targetRoot,
      })
      setReport(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const severityIcon = (s: string) => {
    if (s === "error") return <XCircle className="w-4 h-4 text-red-400" />
    if (s === "warning") return <AlertTriangle className="w-4 h-4 text-yellow-400" />
    return <CheckCircle className="w-4 h-4 text-green-400" />
  }

  const severityColor = (s: string) => {
    if (s === "error") return "border-red-500/30 bg-red-500/5"
    if (s === "warning") return "border-yellow-500/30 bg-yellow-500/5"
    return "border-green-500/30 bg-green-500/5"
  }

  return (
    <div className="space-y-3">
      <Button
        onClick={runCheck}
        disabled={loading || sourceDirs.length === 0}
        variant="outline"
        size="sm"
        className="w-full"
      >
        {loading ? (
          <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Checking...</>
        ) : (
          <><Stethoscope className="w-4 h-4 mr-2" /> Run Preflight Check</>
        )}
      </Button>

      {error && (
        <p className="text-xs text-red-400">{error}</p>
      )}

      {report && (
        <Card className={report.ready ? "border-green-500/30" : "border-yellow-500/30"}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              {report.ready ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-yellow-400" />
              )}
              {report.ready ? "Ready" : "Issues found"}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex gap-2 text-xs">
              <Badge variant="outline">{report.summary.scanned_file_count} files</Badge>
              <Badge variant="outline">{report.summary.source_count} sources</Badge>
              {report.summary.error_count > 0 && (
                <Badge variant="destructive">{report.summary.error_count} errors</Badge>
              )}
              {report.summary.warning_count > 0 && (
                <Badge variant="secondary">{report.summary.warning_count} warnings</Badge>
              )}
            </div>
            {report.diagnostics.length > 0 && (
              <div className="space-y-1 mt-2">
                {report.diagnostics.slice(0, 3).map((d, i) => (
                  <div key={i} className={`flex items-start gap-2 p-2 rounded text-xs ${severityColor(d.severity)}`}>
                    {severityIcon(d.severity)}
                    <div>
                      <p className="font-medium">{d.message}</p>
                      {d.hint && <p className="text-muted-foreground">{d.hint}</p>}
                    </div>
                  </div>
                ))}
                {report.diagnostics.length > 3 && (
                  <p className="text-xs text-muted-foreground">+{report.diagnostics.length - 3} more</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
