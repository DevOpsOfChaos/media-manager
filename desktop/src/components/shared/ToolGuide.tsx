import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { X, HelpCircle } from "lucide-react"

interface ToolGuideProps {
  toolId: string
  title: string
  description: string
  tips?: string[]
}

export function ToolGuide({ toolId, title, description, tips }: ToolGuideProps) {
  const t = useT()
  const storageKey = `tool_guide_seen_${toolId}`
  const [dismissed, setDismissed] = useState(() => localStorage.getItem(storageKey) === "true")
  const [showAgain, setShowAgain] = useState(false)

  const dismiss = () => {
    setDismissed(true)
    setShowAgain(false)
    localStorage.setItem(storageKey, "true")
  }

  const MiniButton = (
    <button
      onClick={() => setShowAgain(true)}
      className="fixed bottom-3 right-3 z-30 w-7 h-7 rounded-full bg-muted hover:bg-primary/20 flex items-center justify-center transition-colors shadow-sm"
      title={t("Show guide again", "Anleitung erneut zeigen")}
    >
      <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" />
    </button>
  )

  if (dismissed && !showAgain) return MiniButton

  return (
    <>
      <Card className="mb-4 border-blue-200 dark:border-blue-800 bg-blue-50/50 dark:bg-blue-950/20">
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-blue-800 dark:text-blue-300">{title}</h3>
              <p className="text-xs text-blue-700 dark:text-blue-400 mt-1">{description}</p>
              {tips && tips.length > 0 && (
                <ul className="mt-2 space-y-0.5">
                  {tips.map((tip, i) => (
                    <li key={i} className="text-[11px] text-blue-600 dark:text-blue-400 flex gap-1.5">
                      <span className="text-blue-400">-</span> {tip}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <Button variant="ghost" size="icon" className="h-6 w-6 shrink-0" onClick={dismiss}>
              <X className="h-3 w-3" />
            </Button>
          </div>
        </CardContent>
      </Card>
      {MiniButton}
    </>
  )
}
