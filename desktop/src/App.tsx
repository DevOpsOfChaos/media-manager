import { useEffect, useState } from "react"
import { useNavigate, useLocation, Outlet } from "react-router-dom"
import { useSettingsStore } from "@/stores/settings-store"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"
import { AppSidebar } from "@/components/layout/AppSidebar"
import { ErrorBoundary } from "@/components/shared/ErrorBoundary"
import { ProgressOverlay } from "@/components/shared/ProgressOverlay"
import { CommandPalette } from "@/components/shared/CommandPalette"
import { NotificationSystem } from "@/components/shared/NotificationSystem"
import { KeyboardShortcuts } from "@/components/shared/KeyboardShortcuts"

function App() {
  const { settings, loaded: settingsLoaded, load: loadSettings } = useSettingsStore()
  const navigate = useNavigate()
  const location = useLocation()
  const [shortcutsOpen, setShortcutsOpen] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  useEffect(() => {
    if (!settingsLoaded) return
    if (settings.show_onboarding && location.pathname !== "/onboarding") {
      navigate("/onboarding", { replace: true })
    }
  }, [settingsLoaded, settings?.show_onboarding, location.pathname])

  useEffect(() => {
    const handle = (e: KeyboardEvent) => {
      if (e.key === "?" && !e.ctrlKey && !e.metaKey && !e.altKey &&
          !(e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement)) {
        e.preventDefault()
        setShortcutsOpen(true)
      }
    }
    window.addEventListener("keydown", handle)
    return () => window.removeEventListener("keydown", handle)
  }, [])

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <ErrorBoundary>
            <div key={location.pathname} className="page-enter">
              <Outlet />
            </div>
          </ErrorBoundary>
        </SidebarInset>
      </SidebarProvider>
      <ProgressOverlay />
      <CommandPalette />
      <NotificationSystem />
      <KeyboardShortcuts open={shortcutsOpen} onOpenChange={setShortcutsOpen} />
    </TooltipProvider>
  )
}

export default App
