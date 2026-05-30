type ToastType = "success" | "error" | "info"

interface Toast {
  id: string
  type: ToastType
  message: string
}

export type { ToastType, Toast }

const TOAST_DURATION = 4000

let listeners: Array<(toasts: Toast[]) => void> = []
let toasts: Toast[] = []

export function toast(type: ToastType, message: string) {
  const id = Date.now().toString()
  toasts = [...toasts, { id, type, message }]
  listeners.forEach(l => l(toasts))
  setTimeout(() => {
    toasts = toasts.filter(t => t.id !== id)
    listeners.forEach(l => l(toasts))
  }, TOAST_DURATION)
}

export function subscribe(fn: (toasts: Toast[]) => void) {
  listeners.push(fn)
  return () => { listeners = listeners.filter(l => l !== fn) }
}

export function getToasts() { return toasts }
