import { useState, useMemo, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useT } from "@/lib/i18n"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { FolderOpen, FolderSync, Scan, Users, MapPin, Eye, X, Clock, Plus, Trash2, Zap, Activity } from "lucide-react"
import { PageHeader } from "@/components/layout/PageHeader"
import { CameraImport } from "@/components/shared/CameraImport"
import { OnboardingTour } from "@/components/shared/OnboardingTour"
import { backgroundScan, healthScanDirectory, smartAlbumsSuggest } from "@/lib/tauri-bridge"
import { sendNotification, isPermissionGranted, requestPermission } from "@tauri-apps/plugin-notification"

export default function DashboardPage() {
  const t = useT()
  const navigate = useNavigate()

  const greeting = new Date().getHours() < 12 ? t("Good morning!", "Guten Morgen!")
    : new Date().getHours() < 18 ? t("Good afternoon!", "Guten Tag!")
    : t("Good evening!", "Guten Abend!")

  const [lastBackup, setLastBackup] = useState<string | null>(() => localStorage.getItem("last_backup_date"))
  const needsBackup = !lastBackup || (Date.now() - new Date(lastBackup).getTime()) > 7 * 24 * 60 * 60 * 1000

  const [showTour, setShowTour] = useState(() => localStorage.getItem("onboarding_complete") !== "true")

  const [healthResult, setHealthResult] = useState<any>(null)

  const [smartAlbums, setSmartAlbums] = useState<any[]>([])

  useEffect(() => {
    const src = localStorage.getItem("default_source_dir")
    if (!src) return
    smartAlbumsSuggest({ source_dir: src, max_files: 500 })
      .then(r => setSmartAlbums(r.suggestions?.slice(0, 4) || []))
      .catch(() => {})
  }, [])

  const [bgMode, setBgMode] = useState(() => {
    if (localStorage.getItem("background_launched") === "true") return true
    const params = new URLSearchParams(window.location.search)
    return params.get("background") === "true"
  })
  const [startupReport, setStartupReport] = useState<any>(null)

  useEffect(() => {
    if (bgMode) {
      localStorage.removeItem("background_launched")
      runBackgroundCheck()
    }
  }, [])

  const runBackgroundCheck = async () => {
    try {
      const sources = JSON.parse(localStorage.getItem("watch_folders") || "[]")
      if (sources.length === 0) {
        const defSource = localStorage.getItem("default_source_dir")
        if (defSource) sources.push(defSource)
      }
      if (sources.length === 0) return

      const scanResult = await backgroundScan({ source_dirs: sources })

      if (scanResult.total_new > 0) {
        try {
          const permitted = await isPermissionGranted()
          if (permitted) {
            await sendNotification({
              title: "Media Manager",
              body: t(`${scanResult.total_new} new files found`, `${scanResult.total_new} neue Dateien gefunden`),
            })
          } else {
            const result = await requestPermission()
            if (result === "granted") {
              await sendNotification({
                title: "Media Manager",
                body: t(`${scanResult.total_new} new files found`, `${scanResult.total_new} neue Dateien gefunden`),
              })
            }
          }
        } catch {}
      }

      setStartupReport({
        time: new Date().toISOString(),
        new_files: scanResult.total_new,
        modified: scanResult.total_modified,
        total: scanResult.total_scanned,
        scan_duration: scanResult.scan_duration_seconds,
      })
    } catch (e) { console.error("Background check failed:", e) }
  }

  const [watchFolders, setWatchFolders] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem("watch_folders") || "[]") }
    catch { return [] }
  })

  const [scheduledTasks, setScheduledTasks] = useState<Array<{id: string; action: string; schedule: string}>>(() => {
    try { return JSON.parse(localStorage.getItem("scheduled_tasks") || "[]") }
    catch { return [] }
  })
  const [newTaskAction, setNewTaskAction] = useState("Organize")
  const [newTaskSchedule, setNewTaskSchedule] = useState("On app start")

  useEffect(() => {
    localStorage.setItem("scheduled_tasks", JSON.stringify(scheduledTasks))
  }, [scheduledTasks])

  const navItems = useMemo(() => [
    { to: "/library", icon: FolderOpen, label: t("Library", "Bibliothek"), desc: t("Browse media", "Medien durchsuchen") },
    { to: "/organize", icon: FolderSync, label: t("Organize", "Organisieren"), desc: t("Sort files", "Dateien sortieren") },
    { to: "/duplicates", icon: Scan, label: t("Duplicates", "Duplikate"), desc: t("Free up space", "Speicher freigeben") },
    { to: "/people", icon: Users, label: t("People", "Personen"), desc: t("Face recognition", "Gesichtserkennung") },
    { to: "/trips", icon: MapPin, label: t("Trips", "Reisen"), desc: t("Trip collections", "Reise-Sammlungen") },
  ], [t])

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <PageHeader
        title={greeting}
        subtitle={t("What would you like to do?", "Was möchtest du tun?")}
      />

      {/* Quick actions */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {navItems.map(item => (
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

      {/* Startup Report */}
      {bgMode && startupReport && (
        <Card className="border-green-200 bg-green-50/30 mb-4">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Zap className="h-4 w-4 text-green-500" />
              {t("Startup Scan Complete", "Startup-Scan abgeschlossen")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs">
            <p>{t(`Scanned ${startupReport.total} files in ${startupReport.scan_duration}s`, `${startupReport.total} Dateien in ${startupReport.scan_duration}s gescannt`)}</p>
            <p className="text-green-600">{t(`${startupReport.new_files} new files found`, `${startupReport.new_files} neue Dateien gefunden`)}</p>
            <div className="flex gap-2 mt-2">
              <Button size="sm" onClick={() => navigate("/duplicates")}>
                {t("Check for duplicates", "Auf Duplikate prüfen")}
              </Button>
              <Button size="sm" variant="outline" onClick={() => setBgMode(false)}>
                {t("Dismiss", "Schließen")}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Watch folders */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-4 w-4" /> {t("Watch Folders", "Überwachte Ordner")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {watchFolders.length === 0 && (
            <p className="text-xs text-muted-foreground">{t("No folders watched.", "Keine Ordner überwacht.")}</p>
          )}
          {watchFolders.map(f => (
            <div key={f} className="flex items-center justify-between text-xs py-1">
              <span className="truncate">{f}</span>
              <Button variant="ghost" size="icon" className="h-5 w-5"
                onClick={() => {
                  const next = watchFolders.filter(w => w !== f)
                  setWatchFolders(next)
                  localStorage.setItem("watch_folders", JSON.stringify(next))
                }}><X className="h-3 w-3" /></Button>
            </div>
          ))}
          <div className="flex gap-1 mt-2">
            <Input placeholder={t("Add folder...", "Ordner hinzufügen...")} className="text-xs h-7"
              onKeyDown={e => {
                if (e.key === "Enter" && e.currentTarget.value.trim()) {
                  const next = [...watchFolders, e.currentTarget.value.trim()]
                  setWatchFolders(next)
                  localStorage.setItem("watch_folders", JSON.stringify(next))
                  e.currentTarget.value = ""
                }
              }} />
          </div>
        </CardContent>
      </Card>

      {/* Scheduled Tasks */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-4 w-4" /> {t("Scheduled Tasks", "Geplante Aufgaben")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {scheduledTasks.length === 0 && (
            <p className="text-xs text-muted-foreground">{t("No tasks scheduled.", "Keine Aufgaben geplant.")}</p>
          )}
          {scheduledTasks.map(task => (
            <div key={task.id} className="flex items-center justify-between text-xs py-1">
              <span>{task.action} &mdash; {task.schedule}</span>
              <Button variant="ghost" size="icon" className="h-5 w-5"
                onClick={() => {
                  const next = scheduledTasks.filter(t => t.id !== task.id)
                  setScheduledTasks(next)
                }}><Trash2 className="h-3 w-3" /></Button>
            </div>
          ))}
          <div className="flex gap-1 mt-2">
            <select className="text-xs h-7 border rounded px-1 bg-background"
              value={newTaskAction}
              onChange={e => setNewTaskAction(e.target.value)}>
              <option value="Organize">{t("Organize", "Organisieren")}</option>
              <option value="Scan Duplicates">{t("Scan Duplicates", "Duplikate scannen")}</option>
              <option value="Face Scan">{t("Face Scan", "Gesichter scannen")}</option>
            </select>
            <select className="text-xs h-7 border rounded px-1 bg-background"
              value={newTaskSchedule}
              onChange={e => setNewTaskSchedule(e.target.value)}>
              <option value="Daily">{t("Daily", "Täglich")}</option>
              <option value="Weekly">{t("Weekly", "Wöchentlich")}</option>
              <option value="On app start">{t("On app start", "Bei App-Start")}</option>
            </select>
            <Button variant="outline" size="icon" className="h-7 w-7"
              onClick={() => {
                const next = [...scheduledTasks, { id: crypto.randomUUID(), action: newTaskAction, schedule: newTaskSchedule }]
                setScheduledTasks(next)
              }}><Plus className="h-3 w-3" /></Button>
          </div>
        </CardContent>
      </Card>

      {/* Health Scan */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            <Activity className="h-4 w-4" /> {t("File Health", "Datei-Gesundheit")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {healthResult ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${healthResult.health_score >= 90 ? 'bg-green-500' : healthResult.health_score >= 70 ? 'bg-amber-500' : 'bg-red-500'}`} />
                <span className="text-sm font-bold">{healthResult.health_score}%</span>
                <span className="text-xs text-muted-foreground">{t("healthy", "gesund")}</span>
              </div>
              {healthResult.unhealthy_count > 0 && (
                <p className="text-xs text-red-500">{healthResult.unhealthy_count} {t("issues found", "Probleme gefunden")}</p>
              )}
            </div>
          ) : (
            <Button variant="outline" size="sm" onClick={async () => {
              const src = localStorage.getItem("default_source_dir")
              if (!src) return
              const r = await healthScanDirectory({ source_dir: src, max_files: 500 })
              setHealthResult(r)
            }}>{t("Scan health", "Gesundheit prüfen")}</Button>
          )}
        </CardContent>
      </Card>

      {/* Smart Albums */}
      {smartAlbums.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <FolderSync className="h-4 w-4" /> {t("Smart Albums", "Smart-Alben")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2">
              {smartAlbums.map((album, i) => (
                <Card key={i} className="cursor-pointer hover:border-primary/30 p-2"
                  onClick={() => navigate("/library")}>
                  <p className="text-sm font-medium">{album.name}</p>
                  <p className="text-xs text-muted-foreground">{album.file_count} {t("photos", "Fotos")}</p>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

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
