import { AlertTriangle } from "lucide-react"

export function ExtensionMismatchWarning({ extension, detectedType }: { extension: string; detectedType: string }) {
  return (
    <div className="flex items-center gap-1.5 text-xs text-amber-500 bg-amber-50 dark:bg-amber-950/20 px-2 py-1 rounded">
      <AlertTriangle className="h-3 w-3" />
      <span>.{extension} → {detectedType}</span>
    </div>
  )
}
