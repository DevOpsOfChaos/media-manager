import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Cloud, FolderSync, Plus, Trash2 } from "lucide-react"

const CLOUD_PATTERNS: Record<string, { name: string; paths: string[] }> = {
  mac: {
    name: "macOS",
    paths: ["~/Library/CloudStorage", "~/Dropbox", "~/Google Drive", "~/OneDrive"],
  },
  win: {
    name: "Windows",
    paths: [
      "C:\\Users\\%USERNAME%\\Dropbox",
      "C:\\Users\\%USERNAME%\\Google Drive",
      "C:\\Users\\%USERNAME%\\OneDrive",
    ],
  },
  linux: {
    name: "Linux",
    paths: ["~/Dropbox", "~/GoogleDrive", "~/OneDrive"],
  },
}

export function CloudWatchFolders() {
  const t = useT()
  const [folders, setFolders] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem("cloud_watch_folders") || "[]") }
    catch { return [] }
  })
  const [newFolder, setNewFolder] = useState("")

  const addFolder = () => {
    if (!newFolder.trim()) return
    const next = [...folders, newFolder.trim()]
    setFolders(next)
    localStorage.setItem("cloud_watch_folders", JSON.stringify(next))
    setNewFolder("")
  }

  const removeFolder = (index: number) => {
    const next = folders.filter((_, i) => i !== index)
    setFolders(next)
    localStorage.setItem("cloud_watch_folders", JSON.stringify(next))
  }

  const detectFolders = () => {
    const platform = navigator.platform.toLowerCase()
    let patterns: string[] = []
    if (platform.includes("win")) patterns = CLOUD_PATTERNS.win.paths
    else if (platform.includes("mac")) patterns = CLOUD_PATTERNS.mac.paths
    else patterns = CLOUD_PATTERNS.linux.paths

    const username = "mries"
    const detected = patterns
      .map(p => p.replace("%USERNAME%", username).replace("~", "C:\\Users\\" + username))
      .filter(() => true)

    const next = [...new Set([...folders, ...detected])]
    setFolders(next)
    localStorage.setItem("cloud_watch_folders", JSON.stringify(next))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Cloud className="h-4 w-4" />
          {t("Cloud Watch Folders", "Cloud-Überwachungsordner")}
        </CardTitle>
        <CardDescription>
          {t("Monitor cloud storage folders for new photos.", "Cloud-Speicher-Ordner auf neue Fotos überwachen.")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <Button size="sm" variant="outline" onClick={detectFolders} className="text-xs">
          <FolderSync className="h-3 w-3 mr-1" /> {t("Auto-detect", "Auto-Erkennung")}
        </Button>

        {folders.map((folder, i) => (
          <div key={i} className="flex items-center gap-2 text-xs p-1.5 border rounded">
            <Cloud className="h-3 w-3 text-muted-foreground" />
            <span className="flex-1 truncate">{folder}</span>
            <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => removeFolder(i)}>
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        ))}

        <div className="flex gap-1">
          <Input value={newFolder} onChange={e => setNewFolder(e.target.value)}
            placeholder={t("Add folder path...", "Ordnerpfad hinzufügen...")}
            className="text-xs h-7"
            onKeyDown={e => e.key === "Enter" && addFolder()} />
          <Button size="sm" onClick={addFolder} disabled={!newFolder.trim()} className="h-7">
            <Plus className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
