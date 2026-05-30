import { useNavigate } from "react-router-dom"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { useT } from "@/lib/i18n"
import { FolderOpen, Scan, Users, Settings } from "lucide-react"

export function WelcomeDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const t = useT()
  const navigate = useNavigate()

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-xl">{t("Welcome to Media Manager!", "Willkommen bei Media Manager!")}</DialogTitle>
          <DialogDescription>
            {t("Your local-first media workflow assistant. Let's get you started.", "Dein lokaler Medien-Workflow-Assistent. Lass uns loslegen.")}
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 gap-3 mt-4">
          <Button variant="outline" className="h-auto flex-col gap-2 p-4" onClick={() => { navigate("/library"); onClose() }}>
            <FolderOpen className="h-8 w-8" />
            <span className="text-sm font-medium">{t("Browse Library", "Bibliothek durchsuchen")}</span>
            <span className="text-xs text-muted-foreground">{t("View your organized media", "Organisierte Medien ansehen")}</span>
          </Button>
          <Button variant="outline" className="h-auto flex-col gap-2 p-4" onClick={() => { navigate("/organize"); onClose() }}>
            <FolderOpen className="h-8 w-8" />
            <span className="text-sm font-medium">{t("Organize Files", "Dateien organisieren")}</span>
            <span className="text-xs text-muted-foreground">{t("Sort into dated folders", "In datierte Ordner sortieren")}</span>
          </Button>
          <Button variant="outline" className="h-auto flex-col gap-2 p-4" onClick={() => { navigate("/duplicates"); onClose() }}>
            <Scan className="h-8 w-8" />
            <span className="text-sm font-medium">{t("Find Duplicates", "Duplikate finden")}</span>
            <span className="text-xs text-muted-foreground">{t("Free up disk space", "Speicherplatz freigeben")}</span>
          </Button>
          <Button variant="outline" className="h-auto flex-col gap-2 p-4" onClick={() => { navigate("/people"); onClose() }}>
            <Users className="h-8 w-8" />
            <span className="text-sm font-medium">{t("Face Recognition", "Gesichtserkennung")}</span>
            <span className="text-xs text-muted-foreground">{t("Group photos by person", "Fotos nach Person gruppieren")}</span>
          </Button>
        </div>
        <div className="flex justify-between items-center mt-4">
          <Button variant="ghost" size="sm" onClick={() => { navigate("/settings"); onClose() }}>
            <Settings className="h-3 w-3 mr-1" /> {t("Settings", "Einstellungen")}
          </Button>
          <Button variant="ghost" size="sm" onClick={() => {
            localStorage.setItem("onboarding_complete", "true")
            onClose()
          }}>
            {t("Skip for now", "Erstmal \u00FCberspringen")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
