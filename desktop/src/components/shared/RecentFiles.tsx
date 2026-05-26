import { useState, useEffect } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { convertFileSrc } from "@tauri-apps/api/core"
import { Clock } from "lucide-react"

export function RecentFiles() {
  const t = useT()
  const [recent, setRecent] = useState<Array<{path: string; name: string; openedAt: string}>>([])

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem("recently_viewed") || "[]")
      setRecent(stored.slice(0, 8))
    } catch { setRecent([]) }
  }, [])

  if (recent.length === 0) return null

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Clock className="h-4 w-4 text-muted-foreground" />
          {t("Recently Viewed", "K\u00FCrzlich angesehen")}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {recent.map((f, i) => (
            <div key={i} className="shrink-0 w-16 text-center cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => window.open(convertFileSrc(f.path) || "", "_blank")}>
              <div className="w-16 h-16 rounded bg-muted overflow-hidden mb-1">
                <img src={convertFileSrc(f.path) || ""} className="w-full h-full object-cover" alt={f.name} loading="lazy" />
              </div>
              <p className="text-[9px] truncate">{f.name}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export function trackRecentlyViewed(path: string, name: string) {
  try {
    const stored = JSON.parse(localStorage.getItem("recently_viewed") || "[]")
    const filtered = stored.filter((f: { path: string }) => f.path !== path)
    filtered.unshift({ path, name, openedAt: new Date().toISOString() })
    localStorage.setItem("recently_viewed", JSON.stringify(filtered.slice(0, 50)))
  } catch { /* ignore */ }
}
