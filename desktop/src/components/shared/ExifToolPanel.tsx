import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Terminal, Copy } from "lucide-react"

const TEMPLATES = [
  { name: "Read all metadata", cmd: "exiftool -G -a -s {file}" },
  { name: "Show GPS only", cmd: "exiftool -GPS* {file}" },
  { name: "Show dates only", cmd: "exiftool -time:all {file}" },
  { name: "Remove all metadata", cmd: "exiftool -all= {file}" },
  { name: "Set copyright", cmd: 'exiftool -Copyright="Your Name" {file}' },
  { name: "Rename by date", cmd: 'exiftool "-FileName<DateTimeOriginal" -d "%Y%m%d_%%f.%%e" {file}' },
]

export function ExifToolPanel() {
  const t = useT()
  const [command, setCommand] = useState("")
  const [filePath, setFilePath] = useState("")

  const buildCommand = (template: string) => {
    if (filePath) {
      setCommand(template.replace(/\{file\}/g, filePath))
    } else {
      setCommand(template)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(command)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Terminal className="h-4 w-4" />
          {t("ExifTool Command Builder", "ExifTool-Befehlsgenerator")}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input
          value={filePath}
          onChange={e => setFilePath(e.target.value)}
          placeholder={t("File path (optional)", "Dateipfad (optional)")}
          className="text-xs"
        />

        <div className="grid grid-cols-2 gap-1">
          {TEMPLATES.map(tpl => (
            <Button key={tpl.name} variant="outline" size="sm"
              className="text-[10px] h-7 justify-start"
              onClick={() => buildCommand(tpl.cmd)}>
              {tpl.name}
            </Button>
          ))}
        </div>

        {command && (
          <div className="space-y-2">
            <div className="bg-muted p-2 rounded text-xs font-mono break-all">
              {command}
            </div>
            <div className="flex gap-1">
              <Button size="sm" variant="outline" className="text-[10px] h-7"
                onClick={copyToClipboard}>
                <Copy className="h-3 w-3 mr-1" /> {t("Copy", "Kopieren")}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
