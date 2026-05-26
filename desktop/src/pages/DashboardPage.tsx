import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import {
  Card,
  CardContent,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FolderOpen, FolderSync, Scan, Users, MapPin } from "lucide-react"
import { CameraImport } from "@/components/shared/CameraImport"
import { OnboardingTour } from "@/components/shared/OnboardingTour"

export default function DashboardPage() {
  const t = useT()
  const navigate = useNavigate()

  const greeting = new Date().getHours() < 12 ? t("Good morning!", "Guten Morgen!")
    : new Date().getHours() < 18 ? t("Good afternoon!", "Guten Tag!")
    : t("Good evening!", "Guten Abend!")

  const [lastBackup, setLastBackup] = useState<string | null>(() => localStorage.getItem("last_backup_date"))
  const needsBackup = !lastBackup || (Date.now() - new Date(lastBackup).getTime()) > 7 * 24 * 60 * 60 * 1000

  const [showTour, setShowTour] = useState(() => localStorage.getItem("onboarding_complete") !== "true")

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{greeting}</h1>
        <p className="text-muted-foreground">{t("What would you like to do?", "Was möchtest du tun?")}</p>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { to: "/library", icon: FolderOpen, label: t("Library", "Bibliothek"), desc: t("Browse media", "Medien durchsuchen") },
          { to: "/organize", icon: FolderSync, label: t("Organize", "Organisieren"), desc: t("Sort files", "Dateien sortieren") },
          { to: "/duplicates", icon: Scan, label: t("Duplicates", "Duplikate"), desc: t("Free up space", "Speicher freigeben") },
          { to: "/people", icon: Users, label: t("People", "Personen"), desc: t("Face recognition", "Gesichtserkennung") },
          { to: "/trips", icon: MapPin, label: t("Trips", "Reisen"), desc: t("Trip collections", "Reise-Sammlungen") },
        ].map(item => (
          <Card key={item.to} className="hover:border-primary/50 cursor-pointer transition-colors"
            onClick={() => navigate(item.to)} role="button" tabIndex={0}
            onKeyDown={e => e.key === "Enter" && navigate(item.to)}>
            <CardContent className="p-4 text-center space-y-2">
              <item.icon className="h-8 w-8 mx-auto text-primary" />
              <p className="font-medium">{item.label}</p>
              <p className="text-xs text-muted-foreground">{item.desc}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Backup reminder */}
      {needsBackup && (
        <Card className="border-amber-500/30 bg-amber-50 dark:bg-amber-950/10">
          <CardContent className="p-3 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{t("Backup reminder", "Backup-Erinnerung")}</p>
              <p className="text-xs text-muted-foreground">
                {lastBackup ? t(`Last: ${new Date(lastBackup).toLocaleDateString()}`, `Letztes: ${new Date(lastBackup).toLocaleDateString()}`)
                  : t("No backup yet", "Noch kein Backup")}
              </p>
            </div>
            <Button size="sm" onClick={() => {
              localStorage.setItem("last_backup_date", new Date().toISOString())
              setLastBackup(new Date().toISOString())
            }}>{t("Done", "Erledigt")}</Button>
          </CardContent>
        </Card>
      )}

      {/* Tour button */}
      <div className="flex justify-center">
        <Button variant="outline" size="sm" onClick={() => setShowTour(true)}>
          {t("Start tour", "Tour starten")}
        </Button>
      </div>

      {/* Camera import */}
      <CameraImport />

      {/* Onboarding tour */}
      {showTour && <OnboardingTour onClose={() => setShowTour(false)} />}
    </div>
  )
}
