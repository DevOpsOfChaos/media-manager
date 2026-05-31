import { useT } from "@/lib/i18n"
import { Button } from "@/components/ui/button"

function ErrorState({ error, onRetry }: { error: string; onRetry: () => void }) {
  const t = useT()
  return (
    <div className="text-center py-12 space-y-4">
      <div className="text-4xl">⚠️</div>
      <h3 className="text-lg font-medium">{t("Something went wrong", "Etwas ist schiefgelaufen")}</h3>
      <p className="text-sm text-muted-foreground max-w-md mx-auto">{error}</p>
      <div className="flex gap-2 justify-center">
        <Button onClick={onRetry}>{t("Try again", "Erneut versuchen")}</Button>
        <Button variant="outline" onClick={() => window.location.reload()}>{t("Reload app", "App neu laden")}</Button>
      </div>
    </div>
  )
}

export { ErrorState }
