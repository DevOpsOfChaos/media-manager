import { useState, useEffect, useCallback } from "react"
import { convertFileSrc } from "@tauri-apps/api/core"
import { ChevronLeft, ChevronRight, X, Pause, Play } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SlideshowProps {
  files: Array<{ path: string; name: string }>
  startIndex?: number
  onClose: () => void
}

export function Slideshow({ files, startIndex = 0, onClose }: SlideshowProps) {
  const [index, setIndex] = useState(startIndex)
  const [playing, setPlaying] = useState(true)
  const [loaded, setLoaded] = useState(false)

  const next = useCallback(() => setIndex(i => (i + 1) % files.length), [files.length])
  const prev = useCallback(() => setIndex(i => (i - 1 + files.length) % files.length), [files.length])

  useEffect(() => {
    if (!playing || files.length <= 1) return
    const timer = setInterval(next, 4000)
    return () => clearInterval(timer)
  }, [playing, next, files.length])

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowRight": next(); break
        case "ArrowLeft": prev(); break
        case "Escape": onClose(); break
        case " ": e.preventDefault(); setPlaying(p => !p); break
      }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [next, prev, onClose])

  if (files.length === 0) return null

  const file = files[index]

  return (
    <div className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center">
      <button onClick={onClose} className="absolute top-4 right-4 text-white/70 hover:text-white z-10">
        <X className="h-6 w-6" />
      </button>

      <div className="absolute top-4 left-4 text-white/70 text-sm z-10">
        {index + 1} / {files.length}
      </div>

      <div className="absolute bottom-20 left-1/2 -translate-x-1/2 text-white/80 text-sm z-10 bg-black/50 px-3 py-1 rounded-full">
        {file.name}
      </div>

      <img
        src={convertFileSrc(file.path)}
        alt={file.name}
        className="max-w-full max-h-full object-contain select-none"
        onLoad={() => setLoaded(true)}
        style={{ opacity: loaded ? 1 : 0, transition: "opacity 300ms" }}
      />

      {files.length > 1 && (
        <>
          <Button variant="ghost" size="icon" onClick={prev}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white hover:bg-white/10 h-12 w-12">
            <ChevronLeft className="h-8 w-8" />
          </Button>
          <Button variant="ghost" size="icon" onClick={next}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-white/70 hover:text-white hover:bg-white/10 h-12 w-12">
            <ChevronRight className="h-8 w-8" />
          </Button>
        </>
      )}

      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 z-10">
        <Button variant="ghost" size="icon" onClick={() => setPlaying(p => !p)}
          className="text-white/70 hover:text-white hover:bg-white/10 h-8 w-8">
          {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  )
}
