import { useEffect } from "react"
import { listen } from "@tauri-apps/api/event"
import { isPermissionGranted, requestPermission, sendNotification } from "@tauri-apps/plugin-notification"

export function NotificationSystem() {
  useEffect(() => {
    const setup = async () => {
      let permitted = await isPermissionGranted()
      if (!permitted) {
        const result = await requestPermission()
        permitted = result === "granted"
      }
      if (!permitted) return

      const unlisten = await listen<{ label: string; detail?: string }>("operation:completed", async (event) => {
        sendNotification({
          title: event.payload.label,
          body: event.payload.detail === "success" ? "Completed successfully" : `Finished: ${event.payload.detail || "done"}`,
        })
      })
      return () => { unlisten() }
    }
    setup()
  }, [])
  return null
}
