import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useT } from "@/lib/i18n"

const SHORTCUTS = [
  { keys: ["Ctrl", "K"], desc_en: "Command palette", desc_de: "Befehlspalette" },
  { keys: ["?"], desc_en: "Show shortcuts", desc_de: "Shortcuts anzeigen" },
  { keys: ["Ctrl", "O"], desc_en: "Browse library", desc_de: "Bibliothek durchsuchen" },
  { keys: ["Ctrl", "P"], desc_en: "Organize files", desc_de: "Dateien organisieren" },
  { keys: ["Ctrl", "D"], desc_en: "Find duplicates", desc_de: "Duplikate finden" },
  { keys: ["Escape"], desc_en: "Close dialog / Go back", desc_de: "Dialog schließen" },
  { keys: ["←", "→"], desc_en: "Navigate pages", desc_de: "Seiten navigieren" },
  { keys: ["Enter"], desc_en: "Open selected file", desc_de: "Ausgewählte Datei öffnen" },
  { keys: ["Delete"], desc_en: "Delete selected", desc_de: "Auswahl löschen" },
  { keys: ["F2"], desc_en: "Rename selected", desc_de: "Auswahl umbenennen" },
]

export function KeyboardShortcuts({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const t = useT()
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{t("Keyboard Shortcuts", "Tastaturkürzel")}</DialogTitle>
        </DialogHeader>
        <div className="space-y-1.5 max-h-80 overflow-y-auto">
          {SHORTCUTS.map((s, i) => (
            <div key={i} className="flex items-center justify-between text-sm py-1">
              <span className="text-muted-foreground">{t(s.desc_en, s.desc_de)}</span>
              <div className="flex gap-1">
                {s.keys.map(k => (
                  <kbd key={k} className="px-1.5 py-0.5 text-[10px] font-mono bg-muted rounded border">
                    {k}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-muted-foreground text-center">
          {t("Press ? anytime to show this dialog", "Drücke ? jederzeit für diese Übersicht")}
        </p>
      </DialogContent>
    </Dialog>
  )
}
