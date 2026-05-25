import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { FolderOpen, Clock, X } from "lucide-react"

const STORAGE_KEY = "recent_paths"
const MAX_RECENT = 8

export function getRecentPaths(): string[] {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]") }
  catch { return [] }
}

export function addRecentPath(path: string) {
  if (!path) return
  const paths = getRecentPaths().filter(p => p !== path)
  paths.unshift(path)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(paths.slice(0, MAX_RECENT)))
}

export function RecentPathsDropdown({ onSelect, currentValue }: { onSelect: (path: string) => void; currentValue?: string }) {
  const [paths, setPaths] = useState<string[]>(getRecentPaths())
  const [open, setOpen] = useState(false)

  useEffect(() => { setPaths(getRecentPaths()) }, [currentValue])

  if (paths.length === 0) return null

  return (
    <div className="relative">
      <Button variant="ghost" size="sm" className="text-xs h-6 gap-1" onClick={() => setOpen(!open)}>
        <Clock className="w-3 h-3" /> Recent
      </Button>
      {open && (
        <div className="absolute top-full left-0 mt-1 w-72 bg-card border border-border rounded-lg shadow-lg z-30 py-1" onMouseLeave={() => setOpen(false)}>
          {paths.map((p, i) => (
            <button
              key={i}
              className="w-full flex items-center gap-2 px-3 py-1.5 text-xs hover:bg-muted/50 text-left truncate"
              onClick={() => { onSelect(p); setOpen(false); addRecentPath(p) }}
            >
              <FolderOpen className="w-3 h-3 text-muted-foreground shrink-0" />
              <span className="truncate">{p}</span>
              <X className="w-3 h-3 ml-auto shrink-0 opacity-0 hover:opacity-100 hover:text-red-400" onClick={e => {
                e.stopPropagation()
                const updated = paths.filter((_, j) => j !== i)
                localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
                setPaths(updated)
              }} />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
