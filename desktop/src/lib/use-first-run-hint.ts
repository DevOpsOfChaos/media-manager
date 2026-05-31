import { useState } from "react"

export function useFirstRunHint(pageName: string): [boolean, () => void] {
  const key = `hint_${pageName}`
  const [showHint, setShowHint] = useState(() => !localStorage.getItem(key))
  const dismiss = () => {
    setShowHint(false)
    localStorage.setItem(key, "true")
  }
  return [showHint, dismiss]
}
