import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"
import { Check, X, RotateCcw } from "lucide-react"

export type FlagState = "none" | "pick" | "reject"

interface PickRejectBarProps {
  flagState: FlagState
  onFlag: (state: FlagState) => void
  compact?: boolean
}

export function PickRejectBar({ flagState, onFlag, compact = false }: PickRejectBarProps) {
  const t = useT()

  return (
    <div className={`flex items-center ${compact ? "gap-0.5" : "gap-1"}`}>
      <Button
        variant={flagState === "pick" ? "default" : "outline"}
        size={compact ? "icon" : "sm"}
        className={`${compact ? "h-6 w-6" : "h-7"} ${flagState === "pick" ? "bg-green-600 hover:bg-green-700" : "hover:bg-green-100 dark:hover:bg-green-900/20 hover:text-green-600"}`}
        onClick={(e) => { e.stopPropagation(); onFlag(flagState === "pick" ? "none" : "pick") }}
        title={t("Pick (P)", "Auswählen (P)")}
      >
        <Check className={compact ? "h-3 w-3" : "h-3.5 w-3.5"} />
      </Button>
      <Button
        variant={flagState === "reject" ? "default" : "outline"}
        size={compact ? "icon" : "sm"}
        className={`${compact ? "h-6 w-6" : "h-7"} ${flagState === "reject" ? "bg-red-600 hover:bg-red-700" : "hover:bg-red-100 dark:hover:bg-red-900/20 hover:text-red-600"}`}
        onClick={(e) => { e.stopPropagation(); onFlag(flagState === "reject" ? "none" : "reject") }}
        title={t("Reject (X)", "Ablehnen (X)")}
      >
        <X className={compact ? "h-3 w-3" : "h-3.5 w-3.5"} />
      </Button>
      {!compact && (
        <Button
          variant="ghost"
          size="sm"
          className="h-7"
          onClick={(e) => { e.stopPropagation(); onFlag("none") }}
          disabled={flagState === "none"}
          title={t("Clear flag (U)", "Markierung löschen (U)")}
        >
          <RotateCcw className="h-3 w-3 mr-1" />
          {t("Clear", "Löschen")}
        </Button>
      )}
    </div>
  )
}
