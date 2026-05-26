import { useState, useRef, useEffect } from "react"
import { invoke } from "@tauri-apps/api/core"
import { Image, Film } from "lucide-react"

interface LazyImageProps {
  path: string
  name: string
  isVideo?: boolean
  className?: string
}

export function LazyImage({ path, name, isVideo, className }: LazyImageProps) {
  const [loaded, setLoaded] = useState(false)
  const [errored, setErrored] = useState(false)
  const [inView, setInView] = useState(false)
  const [dataUrl, setDataUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true)
          observer.disconnect()
        }
      },
      { rootMargin: "200px" }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!inView || dataUrl || loading || isVideo) return
    setLoading(true)
    invoke<string>("read_file_as_data_url", { path })
      .then(url => {
        setDataUrl(url)
        setLoading(false)
      })
      .catch(() => {
        setErrored(true)
        setLoading(false)
      })
  }, [inView, path, dataUrl, loading, isVideo])

  if (isVideo) {
    return (
      <div ref={ref} className={`flex items-center justify-center bg-muted ${className || ""}`}>
        <Film className="w-8 h-8 text-muted-foreground/40" />
      </div>
    )
  }

  return (
    <div ref={ref} className={`bg-muted relative overflow-hidden ${className || ""}`}>
      <div className="absolute inset-0 bg-gradient-to-br from-muted to-muted/50" />

      {(!inView || loading) && !errored && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-muted-foreground/20 border-t-muted-foreground/50 rounded-full animate-spin" />
        </div>
      )}

      {errored && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Image className="w-8 h-8 text-muted-foreground/30" />
        </div>
      )}

      {dataUrl && !errored && (
        <img
          src={dataUrl}
          alt={name}
          className="w-full h-full object-cover absolute inset-0"
          onLoad={() => setLoaded(true)}
          onError={() => setErrored(true)}
          style={{ opacity: loaded ? 1 : 0, transition: "opacity 0.3s" }}
        />
      )}
    </div>
  )
}
