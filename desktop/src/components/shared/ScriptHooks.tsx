import { useState } from "react"
import { useT } from "@/lib/i18n"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Code, Plus, Trash2 } from "lucide-react"

const TRIGGERS = [
  { value: "pre_organize", label_en: "Before Organize", label_de: "Vor Organisieren" },
  { value: "post_organize", label_en: "After Organize", label_de: "Nach Organisieren" },
  { value: "pre_duplicates", label_en: "Before Duplicate Scan", label_de: "Vor Duplikatsuche" },
  { value: "post_duplicates", label_en: "After Duplicate Scan", label_de: "Nach Duplikatsuche" },
  { value: "pre_export", label_en: "Before Export", label_de: "Vor Export" },
  { value: "post_export", label_en: "After Export", label_de: "Nach Export" },
]

export function ScriptHooks() {
  const t = useT()
  const [hooks, setHooks] = useState<Array<{id: string; name: string; trigger: string; command: string}>>(() => {
    try { return JSON.parse(localStorage.getItem("script_hooks") || "[]") }
    catch { return [] }
  })

  const addHook = () => {
    const hook = { id: Date.now().toString(), name: t("New hook", "Neuer Hook"), trigger: "post_organize", command: "echo Done!" }
    const next = [...hooks, hook]
    setHooks(next)
    localStorage.setItem("script_hooks", JSON.stringify(next))
  }

  const removeHook = (id: string) => {
    const next = hooks.filter(h => h.id !== id)
    setHooks(next)
    localStorage.setItem("script_hooks", JSON.stringify(next))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          <Code className="h-4 w-4" />
          {t("Script Hooks", "Skript-Hooks")}
        </CardTitle>
        <CardDescription>
          {t("Run custom scripts before or after operations.", "Eigene Skripte vor oder nach Operationen ausführen.")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        {hooks.map(hook => (
          <div key={hook.id} className="flex items-center gap-2 p-2 border rounded text-xs">
            <Input value={hook.name} onChange={e => {
              const next = hooks.map(h => h.id === hook.id ? {...h, name: e.target.value} : h)
              setHooks(next)
              localStorage.setItem("script_hooks", JSON.stringify(next))
            }} className="text-xs h-7 flex-1" />
            <select value={hook.trigger} onChange={e => {
              const next = hooks.map(h => h.id === hook.id ? {...h, trigger: e.target.value} : h)
              setHooks(next)
              localStorage.setItem("script_hooks", JSON.stringify(next))
            }} className="text-[10px] border rounded px-1 py-0.5 bg-background">
              {TRIGGERS.map(tr => (
                <option key={tr.value} value={tr.value}>{t(tr.label_en, tr.label_de)}</option>
              ))}
            </select>
            <Input value={hook.command} onChange={e => {
              const next = hooks.map(h => h.id === hook.id ? {...h, command: e.target.value} : h)
              setHooks(next)
              localStorage.setItem("script_hooks", JSON.stringify(next))
            }} className="text-xs h-7 w-40 font-mono" />
            <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => removeHook(hook.id)}>
              <Trash2 className="h-3 w-3" />
            </Button>
          </div>
        ))}
        <Button size="sm" variant="outline" onClick={addHook}>
          <Plus className="h-3 w-3 mr-1" /> {t("Add hook", "Hook hinzufügen")}
        </Button>
      </CardContent>
    </Card>
  )
}
