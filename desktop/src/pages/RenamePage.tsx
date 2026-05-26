import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { EmptyState } from "@/components/shared/EmptyState"
import { PreflightCheck } from "@/components/shared/PreflightCheck"
import { ToolGuide } from "@/components/shared/ToolGuide"
import { Pencil, Loader2, Play } from "lucide-react"

// Reuse organize bridge for rename operations since rename uses the same planner
import { organizePreview } from "@/lib/tauri-bridge"
import type { OrganizePreviewResponse } from "@/types"

const RENAME_TEMPLATES = [
  { label: "Date + Original Name", value: "{date:%Y-%m-%d}_{stem}" },
  { label: "Year / Date + Name", value: "{date:%Y}/{date:%Y-%m-%d}_{stem}" },
  { label: "Camera + Date", value: "{camera}/{date:%Y-%m-%d}_{stem}" },
  { label: "Original Name only", value: "{stem}" },
  { label: "Date only", value: "{date:%Y-%m-%d}" },
]

export default function RenamePage() {
  const t = useT()
  const [sourceDir, setSourceDir] = useState(() => localStorage.getItem("default_source_dir") || "")
  const [template, setTemplate] = useState(RENAME_TEMPLATES[0].value)
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState<OrganizePreviewResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handlePreview = async () => {
    if (!sourceDir) return
    setLoading(true); setError(null)
    try {
      const result = await organizePreview({
        source_dirs: [sourceDir],
        target_root: sourceDir,  // rename in-place
        pattern: template,
        operation_mode: "copy",
        include_associated_files: true,
        recursive: true,
        include_hidden: false,
        follow_symlinks: false,
        conflict_policy: "rename",
        include_patterns: [],
        exclude_patterns: [],
        batch_size: 0,
        exiftool_path: "",
      })
      setPreview(result)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <ToolGuide
        toolId="rename"
        title={t("Rename Files", "Dateien umbenennen")}
        description={t("Standardize file names using preset templates or custom patterns with metadata tokens. Preview changes before applying.", "Standardisiere Dateinamen mit Vorlagen oder eigenen Mustern mit Metadaten-Tokens. Vorschau der Änderungen vor der Ausführung.")}
        tips={[
          t("Preview first to verify the new names look correct", "Erst Vorschau anzeigen, um die neuen Namen zu überprüfen"),
          t("Use {date}, {camera}, and {stem} tokens for flexible naming", "Nutze {date}, {camera} und {stem} Tokens für flexible Benennung"),
        ]}
      />
      <div className="flex items-center gap-3">
        <Pencil className="w-6 h-6 text-primary" />
        <div>
          <h1 className="text-xl font-bold">{t("Rename Files", "Dateien umbenennen")}</h1>
          <p className="text-sm text-muted-foreground">{t("Standardize file names using metadata patterns.", "Dateinamen mit Metadaten-Mustern standardisieren.")}</p>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">{t("Source & Pattern", "Quelle & Muster")}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Input value={sourceDir} onChange={e => setSourceDir(e.target.value)} placeholder={t("Source directory", "Quellverzeichnis")} className="text-xs" disabled={loading} />
          <div className="space-y-2">
            <label className="text-xs font-medium">{t("Rename Template", "Umbenennungsvorlage")}</label>
            <div className="grid grid-cols-1 gap-1">
              {RENAME_TEMPLATES.map(t2 => (
                <label key={t2.value} className={`flex items-center gap-2 p-2 rounded cursor-pointer text-xs ${template === t2.value ? 'bg-primary/10 border border-primary/30' : 'hover:bg-muted/50'}`}>
                  <input type="radio" name="template" checked={template === t2.value} onChange={() => setTemplate(t2.value)} />
                  <span className="font-mono text-[11px]">{t2.value}</span>
                  <span className="text-muted-foreground ml-auto">{t(t2.label, t2.label)}</span>
                </label>
              ))}
            </div>
            <Input value={template} onChange={e => setTemplate(e.target.value)} placeholder={t("Custom pattern...", "Eigenes Muster...")} className="text-xs font-mono mt-1" />
          </div>
        </CardContent>
      </Card>

      <PreflightCheck sourceDirs={sourceDir ? [sourceDir] : []} command="rename" />

      <Button onClick={handlePreview} disabled={loading || !sourceDir} size="sm">
        {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}{t("Preview Rename", "Vorschau Umbenennung")}
      </Button>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {preview && (
        <Card className="border-blue-500/30">
          <CardHeader><CardTitle className="text-sm">{t("Preview", "Vorschau")}</CardTitle></CardHeader>
          <CardContent>
            <div className="flex gap-2 mb-3">
              <Badge variant="outline">{preview.planned_count} {t("files", "Dateien")}</Badge>
              <Badge variant="secondary">{preview.skipped_count} {t("skipped", "übersprungen")}</Badge>
              {preview.conflict_count > 0 && <Badge variant="destructive">{preview.conflict_count} {t("conflicts", "Konflikte")}</Badge>}
            </div>
            <div className="max-h-60 overflow-y-auto space-y-1">
              {preview.entries.slice(0, 50).map((e, i) => (
                <div key={i} className="flex justify-between text-xs p-1.5 rounded bg-muted/30">
                  <span className="truncate flex-1">{e.source_path?.split(/[\\/]/).pop()}</span>
                  <span className="text-muted-foreground ml-2">→ {e.target_path?.split(/[\\/]/).pop()}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {!preview && !loading && <EmptyState title={t("No preview yet", "Noch keine Vorschau")} description={t("Select a source directory and a rename template, then click Preview.", "Wählen Sie ein Quellverzeichnis und eine Umbenennungsvorlage, dann klicken Sie Vorschau.")} />}
    </div>
  )
}
