import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { useT } from "@/lib/i18n"

const SHORTCUTS = [
  { keys: ["Ctrl", "K"], desc_en: "Command palette", desc_de: "Befehlspalette" },
  { keys: ["?"], desc_en: "Show shortcuts", desc_de: "Shortcuts anzeigen" },
  { keys: ["Ctrl", "1"], desc_en: "Dashboard", desc_de: "Dashboard" },
  { keys: ["Ctrl", "2"], desc_en: "Library", desc_de: "Bibliothek" },
  { keys: ["Ctrl", "3"], desc_en: "Organize", desc_de: "Organisieren" },
  { keys: ["Ctrl", "4"], desc_en: "Duplicates", desc_de: "Duplikate" },
  { keys: ["Ctrl", "5"], desc_en: "People", desc_de: "Personen" },
  { keys: ["Ctrl", ","], desc_en: "Settings", desc_de: "Einstellungen" },
  { keys: ["Ctrl", "B"], desc_en: "Toggle sidebar", desc_de: "Sidebar umschalten" },
  { keys: ["F11"], desc_en: "Toggle fullscreen", desc_de: "Vollbild umschalten" },
  { keys: ["Escape"], desc_en: "Close dialog / Go back", desc_de: "Dialog schließen" },
  { keys: ["←", "→"], desc_en: "Navigate pages", desc_de: "Seiten navigieren" },
  { keys: ["Enter"], desc_en: "Open selected file", desc_de: "Ausgewählte Datei öffnen" },
  { keys: ["P"], desc_en: "Pick (Library)", desc_de: "Auswählen (Bibliothek)" },
  { keys: ["X"], desc_en: "Reject (Library)", desc_de: "Ablehnen (Bibliothek)" },
  { keys: ["U"], desc_en: "Unflag (Library)", desc_de: "Markierung entfernen (Bibliothek)" },
  { keys: ["F2"], desc_en: "Rename selected", desc_de: "Auswahl umbenennen" },
  { keys: ["Delete"], desc_en: "Delete selected", desc_de: "Auswahl löschen" },
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
