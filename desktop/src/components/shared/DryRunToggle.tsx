import { useT } from "@/lib/i18n"
import { Shield, ShieldAlert } from "lucide-react"

interface DryRunToggleProps {
  enabled: boolean
  onToggle: (enabled: boolean) => void
}

export function DryRunToggle({ enabled, onToggle }: DryRunToggleProps) {
  const t = useT()
  return (
    <button
      onClick={() => onToggle(!enabled)}
      className={`flex items-center gap-1.5 text-[11px] px-2 py-1 rounded-full border transition-colors ${
        enabled
          ? "bg-amber-100 border-amber-300 text-amber-800 dark:bg-amber-900/30 dark:border-amber-700 dark:text-amber-300"
          : "bg-muted/50 border-border text-muted-foreground hover:bg-muted"
      }`}
      title={enabled ? t("Dry-run mode ON \u2014 no files will be modified", "Dry-Run-Modus AN \u2014 keine Dateien werden ver\u00E4ndert") : t("Enable dry-run mode", "Dry-Run-Modus aktivieren")}
    >
      {enabled ? <ShieldAlert className="h-3.5 w-3.5" /> : <Shield className="h-3.5 w-3.5" />}
      {enabled ? t("Dry-Run ON", "Dry-Run AN") : t("Dry-Run", "Dry-Run")}
    </button>
  )
}
