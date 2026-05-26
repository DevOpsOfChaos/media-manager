import { useState, useRef, useEffect } from "react"
import { safeConvertFileSrc } from "@/lib/safe-asset"
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
  const [src, setSrc] = useState<string | null>(null)
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
    if (inView && !src && !isVideo) {
      const url = safeConvertFileSrc(path)
      if (url) {
        setSrc(url)
      } else {
        setErrored(true)
      }
    }
  }, [inView, src, path, isVideo])

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

      {(!inView || errored) && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Image className="w-8 h-8 text-muted-foreground/30" />
        </div>
      )}

      {inView && src && !errored && (
        <img
          src={src}
          alt={name}
          className="w-full h-full object-cover absolute inset-0"
          loading="lazy"
          onLoad={() => setLoaded(true)}
          onError={() => setErrored(true)}
          style={{ opacity: loaded ? 1 : 0, transition: "opacity 0.3s" }}
        />
      )}
    </div>
  )
}
