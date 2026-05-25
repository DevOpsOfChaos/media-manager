import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { libraryBrowse, type LibraryBrowseResult } from "@/lib/tauri-bridge"
import { convertFileSrc } from "@tauri-apps/api/core"
import { EmptyState } from "@/components/shared/EmptyState"
import { FolderOpen, Image, Film, Loader2 } from "lucide-react"

const SUFFIX_COLORS: Record<string, string> = {
  ".jpg": "bg-blue-500/10 text-blue-400", ".jpeg": "bg-blue-500/10 text-blue-400",
  ".png": "bg-green-500/10 text-green-400", ".mp4": "bg-red-500/10 text-red-400",
  ".mov": "bg-red-500/10 text-red-400", ".cr2": "bg-yellow-500/10 text-yellow-400",
  ".cr3": "bg-yellow-500/10 text-yellow-400", ".nef": "bg-yellow-500/10 text-yellow-400",
  ".arw": "bg-yellow-500/10 text-yellow-400", ".dng": "bg-yellow-500/10 text-yellow-400",
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
}

export default function LibraryPage() {
  const [rootDir, setRootDir] = useState(() => localStorage.getItem("library_root") || "")
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<LibraryBrowseResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState("")

  const browse = useCallback(async () => {
    if (!rootDir) return
    setLoading(true); setError(null)
    localStorage.setItem("library_root", rootDir)
    try {
      const r = await libraryBrowse({ root_dir: rootDir })
      setData(r)
    } catch (e) { setError(String(e)) }
    finally { setLoading(false) }
  }, [rootDir])

  const filtered = data?.files.filter(f => !filter || f.name.toLowerCase().includes(filter.toLowerCase()) || f.relative.toLowerCase().includes(filter.toLowerCase())) || []

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center gap-3">
        <FolderOpen className="w-6 h-6 text-primary" />
        <div className="flex-1">
          <h1 className="text-xl font-bold">Library</h1>
          <p className="text-sm text-muted-foreground">Browse your organized media files.</p>
        </div>
      </div>

      <div className="flex gap-2">
        <Input value={rootDir} onChange={e => setRootDir(e.target.value)} placeholder="Root directory (e.g. organized folder)" className="text-xs flex-1" />
        <Button onClick={browse} disabled={loading || !rootDir} size="sm">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Browse"}
        </Button>
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {data && (
        <>
          <div className="flex items-center gap-2">
            <Badge variant="outline">{data.file_count} files</Badge>
            <Input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Filter by name..." className="text-xs w-48" />
          </div>

          {filtered.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
              {filtered.slice(0, 500).map((f, i) => (
                <Card key={i} className="overflow-hidden hover:border-primary/30 transition-colors cursor-pointer group">
                  <div className="aspect-square bg-muted relative overflow-hidden">
                    {[".jpg",".jpeg",".png",".webp",".bmp",".gif",".tiff"].includes(f.suffix) ? (
                      <img src={convertFileSrc(f.path)} alt={f.name} className="w-full h-full object-cover" loading="lazy" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        {[".mp4",".mov"].includes(f.suffix) ? <Film className="w-8 h-8 text-muted-foreground/40" /> : <Image className="w-8 h-8 text-muted-foreground/40" />}
                      </div>
                    )}
                  </div>
                  <CardContent className="p-2">
                    <p className="text-[11px] font-medium truncate" title={f.name}>{f.name}</p>
                    <div className="flex items-center justify-between mt-1">
                      <Badge className={`text-[9px] px-1 py-0 ${SUFFIX_COLORS[f.suffix] || "bg-muted text-muted-foreground"}`}>{f.suffix}</Badge>
                      <span className="text-[10px] text-muted-foreground">{formatSize(f.size)}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState title={filter ? "No matches" : "No files found"} description={filter ? "Try a different filter." : "The directory is empty or contains no supported media files."} />
          )}
        </>
      )}

      {!data && !loading && (
        <EmptyState title="No directory selected" description="Enter a root directory above and click Browse to explore your library." />
      )}
    </div>
  )
}
