import { useState } from "react"
import { useT } from "@/lib/i18n"
import { convertFileSrc } from "@tauri-apps/api/core"
import { X, ArrowLeftRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SplitViewProps {
  files: Array<{ path: string; name: string }>
  onClose: () => void
}

const MAX_SPLIT_FILES = 200

export function SplitView({ files, onClose }: SplitViewProps) {
  const t = useT()
  const safeFiles = files.slice(0, MAX_SPLIT_FILES)
  const [leftIndex, setLeftIndex] = useState(0)
  const [rightIndex, setRightIndex] = useState(Math.min(1, safeFiles.length - 1))

  if (safeFiles.length < 2) return null

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 bg-black/60 text-white">
        <div className="flex items-center gap-2 text-xs">
          <span className="opacity-70">{t("Split View", "Geteilte Ansicht")}</span>
          <span className="opacity-40">|</span>
          <span>{safeFiles[leftIndex]?.name}</span>
          <ArrowLeftRight className="h-3 w-3 opacity-40" />
          <span>{safeFiles[rightIndex]?.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <select value={leftIndex} onChange={e => setLeftIndex(Number(e.target.value))}
            className="text-xs bg-white/10 border border-white/20 rounded px-1 py-0.5">
            {safeFiles.map((f, i) => <option key={i} value={i}>{f.name}</option>)}
          </select>
          <select value={rightIndex} onChange={e => setRightIndex(Number(e.target.value))}
            className="text-xs bg-white/10 border border-white/20 rounded px-1 py-0.5">
            {safeFiles.map((f, i) => <option key={i} value={i}>{f.name}</option>)}
          </select>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-white/70 hover:text-white">
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 flex">
        <div className="flex-1 flex items-center justify-center bg-black/40 p-4">
          <img src={convertFileSrc(safeFiles[leftIndex]?.path)} alt={safeFiles[leftIndex]?.name}
            className="max-w-full max-h-full object-contain" />
        </div>
        <div className="w-px bg-white/20" />
        <div className="flex-1 flex items-center justify-center bg-black/40 p-4">
          <img src={convertFileSrc(safeFiles[rightIndex]?.path)} alt={safeFiles[rightIndex]?.name}
            className="max-w-full max-h-full object-contain" />
        </div>
      </div>

      <div className="text-center py-1 text-white/40 text-[10px]">
        {t("\u2190 \u2192 to navigate | Esc to close", "\u2190 \u2192 zum Navigieren | Esc zum Schlie\u00dfen")}
      </div>
    </div>
  )
}
