import { useState, useEffect, useCallback, useRef } from "react"
import { safeConvertFileSrc } from "@/lib/safe-asset"
import { ChevronLeft, ChevronRight, X, Pause, Play, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useT } from "@/lib/i18n"

interface SlideshowProps {
  files: Array<{ path: string; name: string }>
  startIndex?: number
  onClose: () => void
}

const MAX_SLIDESHOW_FILES = 500

export function Slideshow({ files, startIndex = 0, onClose }: SlideshowProps) {
  const t = useT()
  const safeFiles = files.slice(0, MAX_SLIDESHOW_FILES)
  const [index, setIndex] = useState(Math.min(startIndex, safeFiles.length - 1))
  const [playing, setPlaying] = useState(true)
  const [loaded, setLoaded] = useState(false)
  const [errored, setErrored] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  const next = useCallback(() => {
    setLoaded(false)
    setErrored(false)
    setIndex(i => (i + 1) % safeFiles.length)
  }, [safeFiles.length])

  const prev = useCallback(() => {
    setLoaded(false)
    setErrored(false)
    setIndex(i => (i - 1 + safeFiles.length) % safeFiles.length)
  }, [safeFiles.length])

  useEffect(() => {
    if (!playing || safeFiles.length <= 1) return
    const timer = setInterval(next, 4000)
    return () => clearInterval(timer)
  }, [playing, next, safeFiles.length])

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") next()
      else if (e.key === "ArrowLeft") prev()
      else if (e.key === "Escape") onClose()
      else if (e.key === " ") { e.preventDefault(); setPlaying(p => !p) }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [next, prev, onClose])

  if (safeFiles.length === 0) return null

  const file = safeFiles[index]
  const src = safeConvertFileSrc(file.path) || ""

  return (
    <div className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center">
      <button onClick={onClose} className="absolute top-4 right-4 text-white/70 hover:text-white z-10">
        <X className="h-6 w-6" />
      </button>

      <div className="absolute top-4 left-4 text-white/70 text-sm z-10 flex items-center gap-2">
        <span>{index + 1} / {safeFiles.length}</span>
        {files.length > MAX_SLIDESHOW_FILES && (
          <span className="text-yellow-400 text-xs">({t("first 500 shown", "erste 500")})</span>
        )}
      </div>

      <div className="absolute bottom-20 left-1/2 -translate-x-1/2 text-white/80 text-sm z-10 bg-black/50 px-3 py-1 rounded-full max-w-md truncate">
        {file.name}
      </div>

      <div className="max-w-full max-h-full flex items-center justify-center">
        {errored ? (
          <div className="text-center text-white/60 space-y-2 p-8">
            <AlertTriangle className="h-12 w-12 mx-auto text-yellow-500" />
            <p className="text-sm">{t("Could not load image", "Bild konnte nicht geladen werden")}</p>
            <p className="text-xs text-white/40 max-w-xs truncate">{file.name}</p>
            <Button variant="outline" size="sm" onClick={next} className="text-white/70 hover:text-white">
              {t("Skip", "Überspringen")} →
            </Button>
          </div>
        ) : (
          <img
            ref={imgRef}
            src={src}
            alt={file.name}
            className="max-w-full max-h-full object-contain select-none"
            onLoad={() => setLoaded(true)}
            onError={() => setErrored(true)}
            style={{
              opacity: loaded ? 1 : 0,
              transition: "opacity 300ms",
              maxWidth: "100vw",
              maxHeight: "90vh",
            }}
          />
        )}
      </div>

      {!loaded && !errored && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        </div>
      )}

      {safeFiles.length > 1 && (
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
        {files.length > MAX_SLIDESHOW_FILES && (
          <span className="text-yellow-400 text-[10px]">{t("500 limit", "500er Limit")}</span>
        )}
      </div>
    </div>
  )
}
