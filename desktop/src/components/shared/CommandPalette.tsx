import { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { Search } from "lucide-react"

const COMMANDS = [
  { label: "Organize Files", path: "/organize", keys: "Ctrl+O" },
  { label: "Rename Files", path: "/rename", keys: "Ctrl+R" },
  { label: "Find Duplicates", path: "/duplicates", keys: "Ctrl+D" },
  { label: "People & Faces", path: "/people", keys: "Ctrl+P" },
  { label: "Trip Collection", path: "/trip", keys: "Ctrl+T" },
  { label: "Workflow Runner", path: "/workflow", keys: "Ctrl+W" },
  { label: "Library Browser", path: "/library", keys: "Ctrl+L" },
  { label: "Run History", path: "/history", keys: "Ctrl+H" },
  { label: "Review Workbench", path: "/review" },
  { label: "Settings", path: "/settings", keys: "Ctrl+," },
  { label: "Dashboard", path: "/", keys: "Ctrl+K" },
]

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const [selectedIndex, setSelectedIndex] = useState(0)
  const navigate = useNavigate()

  const filtered = COMMANDS.filter(c => c.label.toLowerCase().includes(query.toLowerCase()))

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault()
        setOpen(prev => !prev)
        setQuery("")
        setSelectedIndex(0)
      }
      if (e.key === "Escape" && open) {
        setOpen(false)
      }
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [open])

  const execute = useCallback((path: string) => {
    setOpen(false)
    navigate(path)
  }, [navigate])

  useEffect(() => {
    if (!open) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") { e.preventDefault(); setSelectedIndex(i => Math.min(i + 1, filtered.length - 1)) }
      if (e.key === "ArrowUp") { e.preventDefault(); setSelectedIndex(i => Math.max(i - 1, 0)) }
      if (e.key === "Enter" && filtered[selectedIndex]) { execute(filtered[selectedIndex].path) }
    }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [open, filtered, selectedIndex, execute])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-background/60 backdrop-blur-sm" onClick={() => setOpen(false)}>
      <div className="w-full max-w-lg bg-card border border-border rounded-xl shadow-2xl overflow-hidden" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
          <Search className="w-4 h-4 text-muted-foreground" />
          <input
            autoFocus
            value={query}
            onChange={e => { setQuery(e.target.value); setSelectedIndex(0) }}
            placeholder="Type a command..."
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
          <kbd className="text-[10px] px-1.5 py-0.5 rounded border border-border text-muted-foreground">esc</kbd>
        </div>
        <div className="max-h-64 overflow-y-auto py-2">
          {filtered.map((cmd, i) => (
            <button
              key={cmd.path}
              className={`w-full flex items-center justify-between px-4 py-2 text-sm hover:bg-muted/50 transition-colors ${i === selectedIndex ? 'bg-muted' : ''}`}
              onClick={() => execute(cmd.path)}
            >
              <span>{cmd.label}</span>
              {cmd.keys && <kbd className="text-[10px] px-1.5 py-0.5 rounded border border-border text-muted-foreground">{cmd.keys}</kbd>}
            </button>
          ))}
          {filtered.length === 0 && <p className="px-4 py-2 text-sm text-muted-foreground">No commands found</p>}
        </div>
        <div className="flex items-center gap-4 px-4 py-2 border-t border-border text-[10px] text-muted-foreground">
          <span><kbd className="px-1 py-0.5 rounded border border-border">↑↓</kbd> Navigate</span>
          <span><kbd className="px-1 py-0.5 rounded border border-border">Enter</kbd> Select</span>
          <span><kbd className="px-1 py-0.5 rounded border border-border">Esc</kbd> Close</span>
        </div>
      </div>
    </div>
  )
}
