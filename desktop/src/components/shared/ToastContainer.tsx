import { useState, useEffect } from "react"
import { subscribe, type Toast } from "@/lib/toast"
import { Check, X, Info } from "lucide-react"

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([])

  useEffect(() => subscribe(setToasts), [])

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map(t => (
        <div key={t.id} className={`flex items-center gap-2 px-4 py-2 rounded-lg shadow-lg text-sm animate-in slide-in-from-right ${
          t.type === "success" ? "bg-green-600 text-white" :
          t.type === "error" ? "bg-red-600 text-white" :
          "bg-blue-600 text-white"
        }`}>
          {t.type === "success" ? <Check className="h-4 w-4" /> :
           t.type === "error" ? <X className="h-4 w-4" /> :
           <Info className="h-4 w-4" />}
          {t.message}
        </div>
      ))}
    </div>
  )
}
