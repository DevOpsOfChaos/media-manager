import { useState } from "react"

const MAX_VISIBLE_HINTS = 2

export function useFirstRunHint(pageName: string): [boolean, () => void] {
  const key = `hint_${pageName}`
  const [dismissed, setDismissed] = useState(() => !!localStorage.getItem(key))

  const visibleCount = typeof document !== "undefined"
    ? document.querySelectorAll("[data-hint]").length
    : 0
  const showHint = !dismissed && visibleCount < MAX_VISIBLE_HINTS

  const dismiss = () => {
    setDismissed(true)
    localStorage.setItem(key, "true")
  }
  return [showHint, dismiss]
}
