import { useEffect } from "react"
import { listen } from "@tauri-apps/api/event"
import { isPermissionGranted, requestPermission, sendNotification } from "@tauri-apps/plugin-notification"

function formatSuccessBody(detail: string | undefined): string {
  if (detail === "success" || !detail) return "Completed successfully"

  try {
    const parsed = JSON.parse(detail)
    const parts: string[] = []
    if (parsed.executed_count !== undefined) parts.push(`${parsed.executed_count} processed`)
    if (parsed.planned_count !== undefined) parts.push(`${parsed.planned_count} planned`)
    if (parsed.renamed_count !== undefined) parts.push(`${parsed.renamed_count} renamed`)
    if (parsed.removed !== undefined) parts.push(`${parsed.removed} removed`)
    if (parsed.total_faces !== undefined) parts.push(`${parsed.total_faces} faces found`)
    if (parsed.matched_faces !== undefined) parts.push(`${parsed.matched_faces} matched`)
    if (parsed.file_count !== undefined) parts.push(`${parsed.file_count} files`)
    if (parsed.exact_duplicate_files !== undefined) parts.push(`${parsed.exact_duplicate_files} duplicates`)
    if (parsed.similar_pairs !== undefined) parts.push(`${parsed.similar_pairs} similar pairs`)
    if (parts.length) return parts.join(", ")
  } catch {}

  return `Completed: ${detail}`
}

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
        const body = event.payload.detail === "success"
          ? formatSuccessBody(event.payload.detail)
          : `Finished: ${event.payload.detail || "done"}`
        sendNotification({
          title: event.payload.label,
          body,
        })
      })
      return () => { unlisten() }
    }
    setup()
  }, [])
  return null
}
